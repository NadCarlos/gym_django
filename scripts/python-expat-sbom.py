"""Expose the Expat actually loaded by Python, including statically bundled copies.

The CPE identity follows the Python Software Foundation's release SBOM:
https://www.python.org/ftp/python/3.13.18/Python-3.13.18.tar.xz.spdx.json
Grype supplies the vulnerability data; this script does not maintain a CVE list.
"""

import json
import platform
import pyexpat


version = ".".join(map(str, pyexpat.version_info))
print(json.dumps({
    "bomFormat": "CycloneDX",
    "specVersion": "1.6",
    "version": 1,
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
