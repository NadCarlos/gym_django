#!/usr/bin/env bash
# Read-only inventory. Run in the deployed checkout; never sources .env files.
set -uo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
web=${1:-cermed_web}
db=${2:-cermed_db}
nginx=${3:-cermed_nginx}
status=0

run() {
    printf '\n== %s ==\n' "$1"
    shift
    if ! "$@"; then
        printf 'INCOMPLETE: command failed; inspect this section.\n' >&2
        status=1
    fi
}

run 'UTC' date -u
run 'OS' cat /etc/os-release
run 'Kernel' uname -r
run 'Memory' free -h
run 'Disk' df -h /
run 'Commit' git rev-parse HEAD
run 'Working tree' git status --short
run 'Docker' docker version --format '{{.Server.Version}}'
run 'Compose' docker compose version
run 'Containers' docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
run 'Listening TCP ports' ss -lnt
for container in "$web" "$db" "$nginx"; do
    run "Image identity: $container" docker inspect --format \
        '{{.Name}} image={{.Image}} created={{.Created}}' "$container"
done
run 'Python packages (metadata only)' docker exec -i "$web" python -I -S - \
    < "$script_dir/runtime_inventory.py"
run 'MySQL version and schema size (no records)' docker exec "$db" sh -ec '
    MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --batch --skip-column-names -u root \
      --database="$MYSQL_DATABASE" -e "
        SELECT VERSION();
        SELECT COUNT(*), COALESCE(SUM(DATA_LENGTH + INDEX_LENGTH), 0)
          FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE();"
'
run 'Nginx build' docker exec "$nginx" nginx -V
run 'Production checks (telemetry disabled for this process)' \
    docker exec -e SENTRY_DSN= "$web" python /app/gym/manage.py check --deploy
exit "$status"
