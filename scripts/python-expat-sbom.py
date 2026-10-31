"""Expose the Expat actually loaded by Python, including statically bundled copies.

The CPE identity follows the Python Software Foundation's release SBOM:
https://www.python.org/ftp/python/3.13.18/Python-3.13.18.tar.xz.spdx.json
Grype supplies the vulnerability data; this script does not maintain a CVE list.
"""

import json
import platform
import pyexpat
import re
import sys


version = ".".join(map(str, pyexpat.version_info))
image_id, architecture = sys.argv[1:]
if not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
    raise ValueError("Expected Docker image ID")
print(json.dumps({
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "version": 1,
    "metadata": {"properties": [
        {"name": "cermed:image-id", "value": image_id},
        {"name": "cermed:architecture", "value": architecture},
    ]},
    "components": [{
        "type": "library",
        "name": "expat",
        "version": version,
        "bom-ref": "python-pyexpat",
        "cpe": f"cpe:2.3:a:libexpat_project:libexpat:{version}:*:*:*:*:*:*:*",
        "properties": [
            {"name": "cermed:python-version", "value": platform.python_version()},
            {"name": "cermed:extension-path", "value": pyexpat.__file__},
        ],
    }],
}, indent=2))
