"""Read package metadata without importing application packages or startup hooks.

Run with: python -I -S scripts/runtime_inventory.py
No environment variables, credentials or direct_url metadata are emitted.
"""

import json
import platform
import ssl
import sys
import sysconfig
from importlib.metadata import distributions
from pathlib import Path


def inventory():
    paths = sorted({sysconfig.get_path("purelib"), sysconfig.get_path("platlib")})
    # Python 3.12 with -S does not initialize a virtualenv's sys.prefix.
    prefix = Path(sys.executable).parent.parent
    if (prefix / "pyvenv.cfg").is_file():
        paths = [str(prefix / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages")]
    packages = sorted(
        (
            {"name": dist.metadata["Name"], "version": dist.version}
            for dist in distributions(path=paths)
            if dist.metadata["Name"]
        ),
        key=lambda package: package["name"].lower(),
    )
    return {
        "python": platform.python_version(),
        "openssl": ssl.OPENSSL_VERSION,
        "architecture": platform.machine(),
        "packages": packages,
    }


if __name__ == "__main__":
    print(json.dumps(inventory(), indent=2))
