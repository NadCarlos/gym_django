#!/usr/bin/env bash
# Scan every image, retain every report, and fail if any scan fails.
set -euo pipefail
reviewed=false
if [ "${1:-}" = --accept-reviewed-risk ]; then
    reviewed=true
    shift
    if [ "$#" -ne 4 ]; then
        echo 'Reviewed mode requires REPORT_DIRECTORY WEB_IMAGE NGINX_IMAGE MYSQL_IMAGE' >&2
        exit 2
    fi
fi
if [ "$#" -lt 2 ]; then
    echo 'Usage: bash scripts/scan-upgrade-images.sh REPORT_DIRECTORY IMAGE [IMAGE ...]' >&2
    exit 2
fi
reports=$1
shift
mkdir -p -- "$reports"
reports=$(cd -- "$reports" && pwd)
scanner=anchore/grype:v0.121.0@sha256:621d56d1d68106b787022c81546f7e0a36202a25d1239f0c20195fab8c16f7ea
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
status=0
index=0
roles=(web nginx mysql)
threshold=(--fail-on high)
if [ "$reviewed" = true ]; then threshold=(); fi
for image in "$@"; do
    index=$((index + 1))
    image_id=$(docker image inspect --format '{{.Id}}' "$image")
    architecture=$(docker image inspect --format '{{.Architecture}}' "$image")
    rm -f -- "$reports/python-expat-$index.json" "$reports/python-expat-$index.cdx.json"
    printf 'Scanning %s -> %s/image-%s.json\n' "$image" "$reports" "$index"
    if ! docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock:ro \
        -v cermed-upgrade-grype-cache:/cache \
        --mount "type=bind,src=$repo_root/config/grype.yaml,dst=/config/grype.yaml,readonly" \
        -e GRYPE_DB_CACHE_DIR=/cache \
        "$scanner" "docker:$image" --config /config/grype.yaml "${threshold[@]}" -o json \
        > "$reports/image-$index.json"; then
        status=1
    elif [ "$reviewed" = true ]; then
        python3 "$repo_root/scripts/check_image_risk.py" \
            --report "$reports/image-$index.json" --scope image \
            --policy "$repo_root/config/reviewed-image-risk.json" \
            --role "${roles[$((index - 1))]}" --image-id "$image_id" || status=1
    fi
    # Image package catalogs can miss Expat compiled into CPython. Inventory
    # the loaded version and scan its upstream CPE as a separate SBOM as well.
    native_status=0
    docker run --rm --read-only --network none -i --entrypoint sh "$image" -ec '
        if command -v python3 >/dev/null 2>&1; then exec python3 - "$1" "$2"; fi
        exit 3
    ' sh "$image_id" "$architecture" < "$repo_root/scripts/python-expat-sbom.py" \
        > "$reports/python-expat-$index.cdx.json" || native_status=$?
    case "$native_status" in
        0)
            printf 'Scanning Python Expat in %s\n' "$image"
            if ! docker run --rm \
                -v cermed-upgrade-grype-cache:/cache \
                --mount "type=bind,src=$reports/python-expat-$index.cdx.json,dst=/sbom.json,readonly" \
                --mount "type=bind,src=$repo_root/config/grype.yaml,dst=/config/grype.yaml,readonly" \
                -e GRYPE_DB_CACHE_DIR=/cache \
                "$scanner" sbom:/sbom.json --config /config/grype.yaml "${threshold[@]}" -o json \
                > "$reports/python-expat-$index.json"; then
                status=1
            elif [ "$reviewed" = true ]; then
                python3 "$repo_root/scripts/check_image_risk.py" \
                    --report "$reports/python-expat-$index.json" --scope python-expat \
                    --sbom "$reports/python-expat-$index.cdx.json" \
                    --policy "$repo_root/config/reviewed-image-risk.json" \
                    --role "${roles[$((index - 1))]}" --image-id "$image_id" || status=1
            fi
            ;;
        3)
            rm -- "$reports/python-expat-$index.cdx.json"
            if [ "$reviewed" = true ] && [ "${roles[$((index - 1))]}" != mysql ]; then
                echo 'BLOCKED: expected Python runtime is missing' >&2
                status=1
            fi
            printf 'No Python interpreter in %s; image scan still applies.\n' "$image"
            ;;
        *)
            printf 'Failed to inventory Python Expat in %s\n' "$image" >&2
            status=1
            ;;
    esac
done
exit "$status"
