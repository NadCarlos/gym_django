#!/usr/bin/env bash
# Exercise the shipped ORM, dump and restore clients against disposable MySQL.
set -euo pipefail
web_image=${1:?Usage: bash scripts/check-mysql-client.sh WEB_IMAGE MYSQL_IMAGE}
db_image=${2:?Missing MYSQL_IMAGE}
work=$(mktemp -d)
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
network=
database=
web=
cleanup() {
    [ -z "$web" ] || docker rm -f "$web" >/dev/null 2>&1 || true
    [ -z "$database" ] || docker rm -f -v "$database" >/dev/null
    [ -z "$network" ] || docker network rm "$network" >/dev/null
    rm -rf -- "$work"
}
trap cleanup EXIT
bash "$repo_root/scripts/create-mysql-tls.sh" "$work/tls" db84 >/dev/null
bash "$repo_root/scripts/create-mysql-tls.sh" "$work/untrusted" db84 >/dev/null
network=$(docker network create --internal "cermed-client-check-${work##*/}")
database=$(docker run -d --network "$network" --network-alias db84 --network-alias wrong-name \
    -e MYSQL_ROOT_PASSWORD=client-check-only -e MYSQL_DATABASE=cermed_rehearsal \
    -e MYSQL_USER=clientcheck -e MYSQL_PASSWORD=client-check-only \
    --mount "type=bind,src=$work/tls/server,dst=/run/mysql-tls/server,readonly" \
    --health-cmd='MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -h 127.0.0.1 -u root -e "SELECT 1"' \
    --health-interval=2s --health-timeout=3s --health-retries=30 \
    "$db_image" --innodb-buffer-pool-size=128M --performance-schema=OFF \
    --ssl-ca=/run/mysql-tls/server/ca.pem --ssl-cert=/run/mysql-tls/server/server-cert.pem \
    --ssl-key=/run/mysql-tls/server/server-key.pem --require-secure-transport=ON)
ready=false
for attempt in {1..60}; do
    if [ "$(docker inspect --format '{{.State.Health.Status}}' "$database")" = healthy ]; then
        ready=true
        break
    fi
    sleep 1
done
if [ "$ready" != true ]; then
    echo 'FAIL: disposable MySQL did not become healthy' >&2
    exit 1
fi
# The app user has privileges only on the fixture and Django test databases.
docker exec "$database" sh -ec 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -u root -e "GRANT ALL ON test_cermed_rehearsal.* TO '\''clientcheck'\''@'\''%'\''"'
web="cermed-client-check-web-${work##*/}"
docker run --rm -i --name "$web" --network "$network" --workdir /app/gym \
    --mount "type=bind,src=$work/tls/client,dst=/run/mysql-tls/client,readonly" \
    --mount "type=bind,src=$work/tls/client/client.cnf,dst=/etc/mysql/conf.d/cermed-tls.cnf,readonly" \
    --mount "type=bind,src=$work/untrusted/client/ca.pem,dst=/run/mysql-tls/untrusted-ca.pem,readonly" \
    -e DJANGO_SETTINGS_MODULE=gym.settings -e SENTRY_DSN= \
    -e WRITE_DB_INSTRUMENTATION_ENABLED=False -e REQUEST_INSTRUMENTATION_ENABLED=False \
    -e MYSQL_SSL_CA=/run/mysql-tls/client/ca.pem \
    -e MYSQL_HOST=db84 -e MYSQL_PORT=3306 -e MYSQL_DATABASE=cermed_rehearsal \
    -e MYSQL_USER=clientcheck -e MYSQL_PASSWORD=client-check-only \
    --entrypoint python "$web_image" - <<'PY'
from datetime import datetime
from decimal import Decimal
from copy import deepcopy
import os
import subprocess

import django
django.setup()
from django.core.management import call_command
from django.db import connection
from django.db.backends.mysql.base import DatabaseWrapper
from django.db.utils import OperationalError

# Verify the actual Django connection settings and actual shipped CLI, not mocks.
for host, ca in [
    ("wrong-name", "/run/mysql-tls/client/ca.pem"),
    ("db84", "/run/mysql-tls/untrusted-ca.pem"),
    ("db84", "/run/mysql-tls/missing-ca.pem"),
]:
    config = deepcopy(connection.settings_dict)
    config["HOST"] = host
    config["OPTIONS"]["ssl"]["ca"] = ca
    probe = DatabaseWrapper(config, alias="tls-negative")
    try:
        probe.ensure_connection()
    except OperationalError as error:
        if error.args[0] != 2026:
            raise
    else:
        raise RuntimeError("ORM accepted an invalid TLS identity")
    finally:
        probe.close()
    result = subprocess.run(
        ["mysql", "--host=" + host, "--ssl-ca=" + ca, "--user=clientcheck", "-e", "SELECT 1"],
        env={**os.environ, "MYSQL_PWD": "client-check-only"}, capture_output=True, text=True,
    )
    if result.returncode == 0 or "ERROR 2026" not in result.stderr:
        raise RuntimeError("CLI did not reject the invalid TLS identity")
result = subprocess.run(
    ["mysql", "--host=db84", "--skip-ssl", "--user=clientcheck", "-e", "SELECT 1"],
    env={**os.environ, "MYSQL_PWD": "client-check-only"}, capture_output=True, text=True,
)
if result.returncode == 0 or "ERROR 3159" not in result.stderr:
    raise RuntimeError("MySQL did not reject unencrypted TCP")
print("PASS: ORM/CLI reject wrong hostname, wrong/missing CA; server rejects unencrypted TCP.")

with connection.cursor() as cursor:
    cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_cipher'")
    if not cursor.fetchone()[1]:
        raise RuntimeError("ORM connection is not encrypted")
    cursor.execute("SHOW TABLES")
    if cursor.fetchall():
        raise RuntimeError("Client check requires a fresh, empty database")
    cursor.execute("""CREATE TABLE client_probe (
        id INT PRIMARY KEY, text_value LONGTEXT, amount DECIMAL(12,2),
        moment DATETIME(6), binary_value LONGBLOB, optional_value VARCHAR(20)
    ) CHARACTER SET utf8mb4""")
    expected = (
        1, "Río Cuarto — ensayo ' \\ 😀", Decimal("1234.56"),
        datetime(2026, 10, 31, 12, 30, 45, 123456), b"\x00\xff\x27\x5c", None,
    )
    cursor.execute("INSERT INTO client_probe VALUES (%s,%s,%s,%s,%s,%s)", expected)
    cursor.execute("SELECT * FROM client_probe")
    if cursor.fetchone() != expected:
        raise RuntimeError("ORM driver changed the synthetic fixture")
    cursor.execute("CREATE VIEW client_probe_view AS SELECT id, text_value FROM client_probe")

call_command("dbbackup", output_filename="client-roundtrip.sql", verbosity=0)
with connection.cursor() as cursor:
    cursor.execute("DROP VIEW client_probe_view")
    cursor.execute("DROP TABLE client_probe")
call_command("dbrestore", input_filename="client-roundtrip.sql", interactive=False, verbosity=0)
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM client_probe")
    if cursor.fetchall() != (expected,):
        raise RuntimeError("Backup/restore did not preserve synthetic data")
    cursor.execute("SELECT id, text_value FROM client_probe_view")
    if cursor.fetchone() != expected[:2]:
        raise RuntimeError("Backup/restore did not preserve the view")
print("PASS: ORM, Django dbbackup/dbrestore, Unicode, binary, decimals, datetime, NULL and view.")
call_command("test", "administracion", "rehabilitacion", "finanzas", "entrada", "usuarios", "home", interactive=False)
PY
