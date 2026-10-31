#!/usr/bin/env bash
# Fail if component-absence assumptions behind Grype exceptions change.
set -euo pipefail
web=${1:?Usage: bash scripts/check-image-exceptions.sh WEB_IMAGE NGINX_IMAGE}
proxy=${2:?Missing NGINX_IMAGE}
for image in "$web" "$proxy"; do
    docker run --rm --read-only --network none --entrypoint sh "$image" -ec '
        for tool in getfacl setfacl chacl; do
            if command -v "$tool" >/dev/null 2>&1; then
                echo "Reevaluate CVE-2026-54370: $tool is installed" >&2
                exit 1
            fi
        done
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
echo 'PASS: component absence and exact patched MariaDB client versions.'
