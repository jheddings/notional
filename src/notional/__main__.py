"""Main entry point for notional.

At the moment, this simply prints the current version and exits.
"""

import platform
import sys

import notional

print(f"{notional.__pkgname__}: v{notional.__version__}")
print(f"python: v{sys.version}")
print(f"platform: {platform.platform()}")
