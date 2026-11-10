#!/bin/sh
# Rebuild only CPython's Expat extension, with a private static patched library.
# Inputs are checksum-verified release archives supplied by the Dockerfile.
set -eu
mkdir -p /tmp/expat-src /tmp/python-src /out
tar -xf /tmp/expat.tar.xz -C /tmp/expat-src --strip-components=1
tar -xf /tmp/python.tar.xz -C /tmp/python-src --strip-components=1
cd /tmp/expat-src
./configure --prefix=/opt/expat --disable-shared --enable-static --with-pic \
    --without-xmlwf --without-examples --without-tests
make -j "$(nproc)"
make install
cd /tmp/python-src
CPPFLAGS=-I/opt/expat/include LDFLAGS=-L/opt/expat/lib \
    ./configure --with-system-expat --without-ensurepip
suffix=$(python3-config --extension-suffix)
make -j "$(nproc)" "Modules/pyexpat$suffix" \
    MODULE_PYEXPAT_LDFLAGS='/opt/expat/lib/libexpat.a -lm'
cp "Modules/pyexpat$suffix" /out/
# Test against the existing interpreter before publishing the replacement.
cd /out
python3 -c 'import pyexpat; from xml.etree import ElementTree; assert pyexpat.version_info == (2, 10, 0), pyexpat.EXPAT_VERSION; assert pyexpat.ParserCreate().Parse("<root/>", True) == 1; assert ElementTree.fromstring("<root/>").tag == "root"'
