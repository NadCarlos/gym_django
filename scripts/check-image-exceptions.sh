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
docker run --rm --read-only --network none --workdir /app/gym \
    --env SENTRY_DSN= --entrypoint python "$web" -c '
from gym import settings
assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.mysql", "Reevaluate SQLite exceptions"
'
echo 'PASS: component-absence and production database assumptions.'
