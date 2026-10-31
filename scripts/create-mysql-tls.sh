#!/usr/bin/env bash
# Create a private CA and server certificate outside the repository; never overwrite.
set -euo pipefail
if [ "$#" -lt 2 ]; then
    echo 'Usage: bash scripts/create-mysql-tls.sh NEW_DIRECTORY DB_HOST [DB_HOST ...]' >&2
    exit 2
fi
output=$(realpath -m -- "$1")
shift
# Also works when this script is copied outside the live production checkout.
ancestor=$output
while :; do
    if [ -f "$ancestor/.git/HEAD" ] || [ -f "$ancestor/.git" ]; then
        echo 'TLS keys must be outside a Git working tree.' >&2
        exit 2
    fi
    [ "$ancestor" != / ] || break
    ancestor=$(dirname -- "$ancestor")
done
names=
for host in "$@"; do
    if [[ ! "$host" =~ ^[[:alnum:]][[:alnum:]_.-]*$ ]]; then
        echo 'Use DNS names, without wildcards, ports or OpenSSL syntax.' >&2
        exit 2
    fi
    kind=DNS
    [[ ! "$host" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || kind=IP
    names="${names:+$names,}$kind:$host"
done
umask 077
mkdir -p -- "$(dirname -- "$output")"
mkdir -- "$output" # Refuse existing directories, including symlinks.
trap 'echo "TLS creation failed; inspect the private directory: $output" >&2' ERR
mkdir "$output/authority" "$output/server" "$output/client"
openssl req -x509 -newkey rsa:3072 -nodes -sha256 -days 3650 \
    -subj '/CN=CERMED MySQL private CA' \
    -addext 'basicConstraints=critical,CA:TRUE,pathlen:0' \
    -addext 'keyUsage=critical,keyCertSign,cRLSign' \
    -keyout "$output/authority/ca-key.pem" -out "$output/client/ca.pem" \
    >"$output/authority/generation.log" 2>&1
openssl req -new -newkey rsa:3072 -nodes -sha256 -subj '/CN=CERMED MySQL server' \
    -keyout "$output/server/server-key.pem" -out "$output/authority/server.csr" \
    >>"$output/authority/generation.log" 2>&1
cat > "$output/authority/server.ext" <<EOF
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=$names
EOF
openssl x509 -req -sha256 -days 365 -in "$output/authority/server.csr" \
    -CA "$output/client/ca.pem" -CAkey "$output/authority/ca-key.pem" \
    -set_serial "0x$(openssl rand -hex 16)" -extfile "$output/authority/server.ext" \
    -out "$output/server/server-cert.pem" >>"$output/authority/generation.log" 2>&1
cp "$output/client/ca.pem" "$output/server/ca.pem"
cat > "$output/client/client.cnf" <<'EOF'
[client]
ssl-ca=/run/mysql-tls/client/ca.pem
ssl-verify-server-cert
EOF
# The private outer directory stays 0700. Only MySQL mounts server/; its
# unprivileged UID needs to read the server key. Web mounts public client/ only.
chmod 755 "$output/server" "$output/client"
chmod 644 "$output/server/"*.pem "$output/client/"*
openssl verify -CAfile "$output/client/ca.pem" -purpose sslserver "$output/server/server-cert.pem"
for host in "$@"; do
    check=-checkhost
    [[ ! "$host" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || check=-checkip
    openssl x509 -in "$output/server/server-cert.pem" -noout "$check" "$host"
done
openssl x509 -in "$output/server/server-cert.pem" -noout -enddate
printf 'TLS files created outside the repo: %s\nRenew before expiry; never mount authority/ in a container.\n' "$output"
