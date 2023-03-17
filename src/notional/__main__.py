"""Main entry point for notional.

At the moment, this simply prints the current version and exits.
"""

import platform
import sys

from notional import version

print(f"{version.__pkgname__}: v{version.__version__}")
print(f"python: v{sys.version}")
print(f"platform: {platform.platform()}")
