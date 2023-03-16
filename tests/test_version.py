"""Unit tests for Notional version information."""

import logging
import re
import subprocess
import sys
from unittest import mock

from notional import version

# keep logging output to a minimum for testing
logging.basicConfig(level=logging.INFO)


def test_basic_version():
    """Ensure basic version information is available."""
    assert version.__pkgname__
    assert version.__version__


def test_version_is_valid_string():
    """Ensure version strings meet expected conventions."""
    assert re.match(r"^[0-9]+(\.[0-9])+(-.*)?$", version.__version__)


def test_module_version():
    """Ensure module version information is available."""
    process = subprocess.run([sys.executable, "-m", "notional"], capture_output=True)

    assert process.returncode == 0
    assert version.__version__ in str(process.stdout)


def test_module_main():
    """Make sure running __main__ includes version information."""

    with mock.patch("builtins.print") as mocked_print:
        import notional.__main__  # noqa: F401

        assert mocked_print.called
