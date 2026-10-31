#!/usr/bin/env bash
# Exercise the production proxy config and renewal entrypoint with disposable TLS.
set -euo pipefail
image=${1:?Usage: bash scripts/check-nginx-image.sh IMAGE}
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=$(mktemp -d)
network=
backend=
proxy=
cleanup() {
    if [ -n "$proxy" ]; then
        docker exec "$proxy" chmod -R a+rwX /etc/letsencrypt >/dev/null 2>&1 || true
        docker rm -f "$proxy" >/dev/null
    fi
    [ -z "$backend" ] || docker rm -f "$backend" >/dev/null
    [ -z "$network" ] || docker network rm "$network" >/dev/null
    rm -rf -- "$work"
}
trap cleanup EXIT
mkdir -p "$work/certs/live/cermed.com.ar" "$work/static" "$work/media" \
    "$work/acme/.well-known/acme-challenge"
printf 'static-ok\n' > "$work/static/probe.txt"
printf 'media-ok\n' > "$work/media/probe.txt"
printf 'acme-ok\n' > "$work/acme/.well-known/acme-challenge/probe"
# Fake public certificate and key, used only inside this disposable test.
openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
    -subj /CN=cermed.com.ar -addext subjectAltName=DNS:cermed.com.ar \
    -keyout "$work/certs/live/cermed.com.ar/privkey.pem" \
    -out "$work/certs/live/cermed.com.ar/fullchain.pem" >/dev/null 2>&1
network=$(docker network create "cermed-proxy-check-${work##*/}")
backend=$(docker run -d --network "$network" --network-alias cermed_web \
    --entrypoint python3 "$image" -m http.server 8000)
proxy=$(docker run -d --network "$network" \
    -p 127.0.0.1::80 -p 127.0.0.1::443 \
    --mount "type=bind,src=$repo_root/config,dst=/app/config,readonly" \
    --mount "type=bind,src=$repo_root/cermed.conf,dst=/etc/nginx/conf.d/cermed.conf,readonly" \
    --mount "type=bind,src=$work/certs,dst=/etc/letsencrypt" \
    --mount "type=bind,src=$work/static,dst=/app/staticfiles,readonly" \
    --mount "type=bind,src=$work/media,dst=/app/media,readonly" \
    --mount "type=bind,src=$work/acme,dst=/var/www/certbot" \
    --entrypoint sh "$image" /app/config/entrypoint.nginx.sh)
http_port=$(docker port "$proxy" 80/tcp | sed 's/.*://')
https_port=$(docker port "$proxy" 443/tcp | sed 's/.*://')
tls=(curl -q --noproxy '*' --silent --show-error --fail --connect-timeout 2 --max-time 5
    --cacert "$work/certs/live/cermed.com.ar/fullchain.pem"
    --resolve "cermed.com.ar:$https_port:127.0.0.1")
ready=false
for attempt in {1..20}; do
    if "${tls[@]}" "https://cermed.com.ar:$https_port/" >/dev/null 2>&1; then
        ready=true
        break
    fi
    sleep 1
done
if [ "$ready" != true ]; then docker logs "$proxy"; exit 1; fi
test "$(curl -q --noproxy '*' --silent --show-error --max-time 5 -o /dev/null \
    -w '%{http_code}' -H 'Host: cermed.com.ar' "http://127.0.0.1:$http_port/")" = 301
test "$("${tls[@]}" "https://cermed.com.ar:$https_port/static/probe.txt")" = static-ok
test "$("${tls[@]}" "https://cermed.com.ar:$https_port/media/probe.txt")" = media-ok
test "$(curl -q --noproxy '*' --silent --show-error --fail --max-time 5 \
    -H 'Host: cermed.com.ar' "http://127.0.0.1:$http_port/.well-known/acme-challenge/probe")" = acme-ok
docker exec "$proxy" /opt/certbot/bin/pip check
docker exec -i "$proxy" /opt/certbot/bin/python - <<'PY'
import bz2
import ctypes
import dbm.gnu
import dbm.ndbm
import lzma
import readline
import sqlite3
import ssl
import sys
import uuid
import zlib

assert sys.version_info[:3] == (3, 13, 18), sys.version
# CVE-2026-19553: check_hostname must not silently allow a missing hostname.
context = ssl.create_default_context()
for hostname in (None, ""):
    try:
        context.wrap_bio(ssl.MemoryBIO(), ssl.MemoryBIO(), server_hostname=hostname)
    except ValueError:
        pass
    else:
        raise AssertionError("TLS accepted an absent server_hostname")
context.wrap_bio(ssl.MemoryBIO(), ssl.MemoryBIO(), server_hostname="example.test")
print("PASS: patched Certbot Python, native imports and TLS hostname guard.")
PY
docker exec "$proxy" certbot --version
docker exec "$proxy" certbot plugins --authenticators | grep -q webroot
docker exec "$proxy" sh -c 'test "$(stat -c %a /etc/cron.d/certbot-renewal)" = 644; kill -0 "$(cat /var/run/crond.pid)"'
# Reproduce cron's PATH, which does not contain /usr/sbin. No renewal configs
# exist here: this checks invocation/reload, not a successful ACME issuance.
docker exec "$proxy" env -i PATH=/usr/bin:/bin HOME=/root \
    /bin/sh /app/config/certbot-renewal.sh
# A failed renewal must preserve its exit status and must not invoke Nginx.
# Only the throwaway container gets these stubs.
docker exec "$proxy" sh -ec 'rm /usr/bin/certbot; printf "#!/bin/sh\nexit 42\n" > /usr/bin/certbot; chmod 755 /usr/bin/certbot; rm /usr/sbin/nginx; printf "#!/bin/sh\ntouch /tmp/unexpected-reload\nexit 99\n" > /usr/sbin/nginx; chmod 755 /usr/sbin/nginx'
status=0
docker exec "$proxy" env -i PATH=/usr/bin:/bin HOME=/root \
    /bin/sh /app/config/certbot-renewal.sh || status=$?
test "$status" = 42
docker exec "$proxy" test ! -f /tmp/unexpected-reload
echo 'PASS: TLS, redirect, proxy, static/media, ACME path, Certbot, cron PATH and renewal failure handling.'
