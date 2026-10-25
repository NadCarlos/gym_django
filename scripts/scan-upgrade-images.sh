#!/usr/bin/env bash
# Scan every image, retain every report, and fail if any scan fails.
set -euo pipefail
if [ "$#" -lt 2 ]; then
    echo 'Usage: bash scripts/scan-upgrade-images.sh REPORT_DIRECTORY IMAGE [IMAGE ...]' >&2
    exit 2
fi
reports=$1
shift
mkdir -p -- "$reports"
scanner=anchore/grype:v0.121.0@sha256:621d56d1d68106b787022c81546f7e0a36202a25d1239f0c20195fab8c16f7ea
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
status=0
index=0
for image in "$@"; do
    index=$((index + 1))
    printf 'Scanning %s -> %s/image-%s.json\n' "$image" "$reports" "$index"
    if ! docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock:ro \
        -v cermed-upgrade-grype-cache:/cache \
        --mount "type=bind,src=$repo_root/config/grype.yaml,dst=/config/grype.yaml,readonly" \
        -e GRYPE_DB_CACHE_DIR=/cache \
        "$scanner" "docker:$image" --config /config/grype.yaml --fail-on high -o json \
        > "$reports/image-$index.json"; then
        status=1
    fi
done
exit "$status"
