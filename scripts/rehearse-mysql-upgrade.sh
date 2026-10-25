#!/usr/bin/env bash
# Import into EMPTY rehearsal schemas only; never connects to production.
set -euo pipefail
if [ "$#" -ne 1 ] || [ ! -s "$1" ]; then
    echo 'Usage: bash scripts/rehearse-mysql-upgrade.sh /protected/path/database.sql' >&2
    exit 2
fi
dump=$(realpath -- "$1")
if grep -Eiq '^([[:space:]]*(CREATE|DROP)[[:space:]]+DATABASE|[[:space:]]*USE[[:space:]])' "$dump"; then
    echo 'Use a single-database mysqldump without --databases/--all-databases or USE statements.' >&2
    exit 2
fi
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
project=${CERMED_REHEARSAL_PROJECT:-cermed-upgrade}
if [[ ! "$project" =~ ^cermed-upgrade(-[a-z0-9-]+)?$ ]]; then
    echo 'Rehearsal project must be cermed-upgrade or start with cermed-upgrade-.' >&2
    exit 2
fi
dc=(docker compose --project-name "$project" --env-file /dev/null -f "$root/docker-compose-upgrade.yaml")
umask 077
work=$(mktemp -d "${TMPDIR:-/tmp}/cermed-mysql-rehearsal.XXXXXX")
printf 'Protected dumps and comparison reports: %s\n' "$work"
active_service=
cleanup() {
    local result=$?
    if [ -n "$active_service" ]; then
        "${dc[@]}" stop "$active_service" || result=1
    fi
    exit "$result"
}
trap cleanup EXIT

sql() {
    local service=$1
    shift
    "${dc[@]}" exec -T "$service" sh -ec \
        'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql --batch --skip-column-names -u root "$MYSQL_DATABASE" "$@"' sh "$@"
}

export_db() {
    local service=$1
    shift
    "${dc[@]}" exec -T "$service" sh -ec \
        'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysqldump -u root --single-transaction --no-tablespaces --default-character-set=utf8mb4 --hex-blob "$@" "$MYSQL_DATABASE"' sh "$@"
}

snapshot() {
    local service=$1 table count digest
    sql "$service" -e "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME" > "$work/$service.tables"
    : > "$work/$service.counts"
    while IFS= read -r table; do
        [[ "$table" =~ ^[a-zA-Z0-9_]+$ ]] || { echo 'Unexpected table identifier' >&2; exit 2; }
        # docker exec reads stdin; keep it from consuming the remaining table list.
        sql "$service" -e "SELECT '$table', COUNT(*) FROM \`$table\`" </dev/null >> "$work/$service.counts"
    done < "$work/$service.tables"
    if [ "$(wc -l < "$work/$service.tables")" != "$(wc -l < "$work/$service.counts")" ]; then
        echo "Incomplete table counts for $service" >&2
        exit 1
    fi
    # Hash normalized row INSERTs, not version-specific dump comments or DDL.
    # awk succeeds for empty databases too; pipefail preserves mysqldump failures.
    export_db "$service" --no-create-info --skip-extended-insert --skip-comments --order-by-primary \
        | awk '/^INSERT INTO /' | LC_ALL=C sort | sha256sum > "$work/$service.rows.sha256"
    sql "$service" -e "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_TYPE='VIEW' ORDER BY TABLE_NAME" > "$work/$service.views"
    : > "$work/$service.view-results"
    while IFS= read -r table; do
        [[ "$table" =~ ^[a-zA-Z0-9_]+$ ]] || { echo 'Unexpected view identifier' >&2; exit 2; }
        count=$(sql "$service" -e "SELECT COUNT(*) FROM \`$table\`" </dev/null)
        digest=$(sql "$service" -e "SELECT * FROM \`$table\`" </dev/null | LC_ALL=C sort | sha256sum)
        printf '%s\t%s\t%s\n' "$table" "$count" "$digest" >> "$work/$service.view-results"
    done < "$work/$service.views"
    if [ "$(wc -l < "$work/$service.views")" != "$(wc -l < "$work/$service.view-results")" ]; then
        echo "Incomplete view checks for $service" >&2
        exit 1
    fi
}

previous=
for service in db57 db80 db84; do
    active_service=$service
    "${dc[@]}" up -d --wait "$service"
    tables=$(sql "$service" -e 'SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()')
    if [ "$tables" != 0 ]; then
        echo "$service is not empty. Refusing to overwrite existing rehearsal data." >&2
        exit 2
    fi
    source_dump=$dump
    if [ -n "$previous" ]; then
        source_dump="$work/$previous.sql"
    fi
    # SQL errors may contain patient data: retain them only in the private log.
    if ! sql "$service" < "$source_dump" > "$work/$service.import.log" 2>&1; then
        echo "Import failed; inspect the private log: $work/$service.import.log" >&2
        exit 1
    fi
    snapshot "$service"
    if [ -n "$previous" ]; then
        diff -u "$work/$previous.tables" "$work/$service.tables"
        diff -u "$work/$previous.counts" "$work/$service.counts"
        diff -u "$work/$previous.rows.sha256" "$work/$service.rows.sha256"
        diff -u "$work/$previous.views" "$work/$service.views"
        diff -u "$work/$previous.view-results" "$work/$service.view-results"
    fi
    export_db "$service" --routines --events --triggers > "$work/$service.sql"
    test -s "$work/$service.sql"
    sql "$service" -e 'SELECT VERSION()'
    "${dc[@]}" stop "$service"
    active_service=
    previous=$service
done
echo 'Rehearsal passed: identical tables, views, counts and row hashes across 5.7 -> 8.0 -> 8.4.'
printf 'Next: make CERMED_REHEARSAL_PROJECT=%s upgrade-check. This is not production migration approval.\n' "$project"
