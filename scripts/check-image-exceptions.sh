#!/usr/bin/env bash
# Fail if component-absence assumptions behind Grype exceptions change.
set -euo pipefail
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
web=${1:?Usage: bash scripts/check-image-exceptions.sh WEB_IMAGE NGINX_IMAGE}
proxy=${2:?Missing NGINX_IMAGE}
for image in "$web" "$proxy"; do
    docker run --rm --read-only --network none --entrypoint sh "$image" -ec '
        test "$(dpkg-query -W -f='"'"'${Version}'"'"' libsqlite3-0)" = "3.54.1-2"
        for tool in getfacl setfacl chacl nsenter infocmp; do
            if command -v "$tool" >/dev/null 2>&1; then
                echo "Reevaluate component-absence filters: $tool is installed" >&2
                exit 1
            fi
        done
    '
    docker run --rm --read-only --network none --entrypoint python3 "$image" -c '
import sqlite3
assert sqlite3.sqlite_version_info == (3, 54, 1), sqlite3.sqlite_version
with sqlite3.connect(":memory:") as connection:
    connection.execute("CREATE VIRTUAL TABLE probe USING fts5(value, detail=none, prefix=2)")
    connection.executemany("INSERT INTO probe(rowid, value) VALUES (?, ?)", [(-1, "patched"), (1, "parser")])
    assert connection.execute("SELECT count(*) FROM probe WHERE probe MATCH ?", ("pa*",)).fetchone() == (2,)
print("PASS: loaded SQLite 3.54.1 and FTS5 query with negative rowids.")
'
done
docker run --rm --read-only --network none --entrypoint sh "$proxy" -ec '
    for module in Pod::Text Archive::Tar; do
        if perl -M"$module" -e 1 >/dev/null 2>&1; then
            echo "Reevaluate Perl exception: $module is installed" >&2
            exit 1
        fi
    done
'
docker run --rm --read-only --network none --entrypoint sh "$web" -ec '
    for package in libmariadb3 mariadb-client mariadb-client-compat mariadb-client-core mariadb-common mysql-common; do
        test "$(dpkg-query -W -f='"'"'${Version}'"'"' "$package")" = "1:11.8.9+maria~deb13"
    done
    if command -v mariadbd >/dev/null 2>&1 || command -v mysqld >/dev/null 2>&1; then
        echo "Unexpected database server in web image; reevaluate client-only filters" >&2
        exit 1
    fi
'
docker run --rm --read-only --network none --entrypoint python "$web" -c '
import MySQLdb
assert MySQLdb.get_client_info() == "3.4.10", "Reevaluate MariaDB Connector/C fixes"
'
docker run --rm --read-only --network none --entrypoint sh "$web" -ec '
    test "$LANG" = es_AR.UTF-8
    test "$LANGUAGE" = es_AR:es
    test "$LC_ALL" = es_AR.UTF-8
'
docker run --rm --read-only --network none --entrypoint sh "$proxy" -ec '
    test "$LANG" = C.UTF-8
    test -z "${LANGUAGE-}"
    test -z "${LC_ALL-}"
'
grep -Fqx 'export LANG=es_AR.UTF-8' "$repo_root/config/entrypoint.prod.sh"
grep -Fqx 'export LANGUAGE=es_AR:es' "$repo_root/config/entrypoint.prod.sh"
grep -Fqx 'export LC_ALL=es_AR.UTF-8' "$repo_root/config/entrypoint.prod.sh"
grep -Fqx 'export LANG=C.UTF-8' "$repo_root/config/entrypoint.nginx.sh"
grep -Fqx 'export LANGUAGE=C' "$repo_root/config/entrypoint.nginx.sh"
grep -Fqx 'export LC_ALL=C.UTF-8' "$repo_root/config/entrypoint.nginx.sh"
echo 'PASS: patched SQLite, component absence, exact patched MariaDB clients and safe locale policy.'
