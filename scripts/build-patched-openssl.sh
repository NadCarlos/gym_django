#!/bin/sh
# Build Debian packages with the published OpenSSL 3.5 security backports.
set -eu
mkdir -p /tmp/openssl-source /out
tar -xf /tmp/openssl.tar.gz -C /tmp/openssl-source --strip-components=1
tar -xf /tmp/openssl-debian.tar.xz -C /tmp/openssl-source
cd /tmp/openssl-source
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

backports = Path('/tmp/openssl-backports')
manifest = json.loads((backports / 'manifest.json').read_text())
series = Path('debian/patches/series')
with series.open('a') as output:
    output.write('\n')
    for entry in manifest['patches']:
        patch = (backports / entry['file']).read_bytes()
        if hashlib.sha256(patch).hexdigest() != entry['sha256']:
            raise ValueError(f"OpenSSL patch checksum mismatch: {entry['file']}")
        name = 'cermed-' + entry['file']
        Path('debian/patches', name).write_bytes(patch)
        output.write(name + '\n')
changelog = Path('debian/changelog')
original = changelog.read_text()
assert original.startswith(f"openssl ({manifest['base_version']})"), 'Unexpected Debian source'
changelog.write_text(
    f"openssl ({manifest['version']}) trixie; urgency=high\n\n"
    "  * CERMED: backport the published upstream security fixes; see manifest.json.\n\n"
    " -- CERMED <noreply@cermed.com.ar>  Wed, 25 Nov 2026 12:00:00 +0000\n\n"
    + original
)
# Run the selected upstream suites during Debian's build, before packaging or
# dpkg-source's after-build cleanup can unapply any quilt patches.
rules = Path('debian/rules')
command = '$(MAKE) -C build_shared test $(TESTSUITE_FLAGS)'
contents = rules.read_text()
assert contents.count(command) == 1, 'Unexpected Debian test target'
rules.write_text(contents.replace(command, command + f' TESTS="{manifest["tests"]}"'))
PY
# Record every patch in Debian's quilt series so the built source is auditable.
dpkg-source --before-build .
# Fail on rejects/fuzz; these are exact upstream 3.5 backports, not guessed fixes.
test -z "$(find . -name '*.rej' -print -quit)"
DEB_BUILD_OPTIONS="parallel=$(nproc)" dpkg-buildpackage -B -us -uc -Pnoudeb
cp /tmp/libssl3t64_*.deb /tmp/libssl-dev_*.deb /tmp/openssl_*.deb \
    /tmp/openssl-provider-legacy_*.deb /out/
