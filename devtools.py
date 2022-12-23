"""Tools that help maintain Notional."""

import os
import shutil
import subprocess

import click

BASEDIR = os.path.dirname(__file__)
SRCDIR = f"{BASEDIR}/src"


################################################################################
## Logging Utilities ##


def echo(msg, fg=None, bg=None):
    """Display a message on the console."""
    styled = click.style("» " + msg, fg=fg, bg=bg)
    click.echo(styled)


def debug(msg):
    """Display a debug message on the console."""
    echo(msg, fg="magenta")


def info(msg):
    """Display an informational message on the console."""
    echo(msg, fg="cyan")


def warn(msg):
    """Display a warning on the console."""
    echo(msg, fg="red")


def alert(msg):
    """Display an alert on the console."""
    echo(msg, fg="black", bg="red")


################################################################################
## Command Utilities ##


def exec(cmd):
    """Execute the given command."""
    subprocess.run(cmd, check=False, shell=False)


def rmdir(path, recurse=True):
    """Remove the given path if needed."""

    if not os.path.exists(path):
        debug(f"{path} does not exist; skipping")

    elif recurse:
        debug(f"removing tree: {path}")
        shutil.rmtree(path)

    else:
        debug(f"removing path: {path}")
        os.rmdir(path)


################################################################################
## preflight ##


@click.command("preflight")
def preflight():
    """Run all preflight checks."""

    info("BEGIN: preflight")

    exec(["pre-commit", "install", "--install-hooks", "--overwrite"])
    exec(["pre-commit", "run", "--all-files", "--verbose"])


################################################################################
## mkdocs ##


@click.command("mkdocs")
def mkdocs():
    """Build documentations."""

    info("BEGIN: mkdocs")
    exec(["mkdocs", "build"])


################################################################################
## utest ##


@click.command("utest")
@click.option(
    "--vcr", "vcr_mode", help="Set the VCR record mode (default: once).", default="once"
)
@click.option(
    "--coverage",
    "-C",
    default=None,
    is_flag=False,
    flag_value="report",
    type=click.Choice(["report", "html"], case_sensitive=False),
    help="Generate a coverage report (default: None).",
)
def run_unit_tests(coverage, vcr_mode):
    """Run unit tests."""

    info("BEGIN: utest")
    debug(f"↳ coverage:{coverage} vcr:{vcr_mode}")

    # TODO look into running pytest natively (e.g. no exec)

    pytest = ["pytest", "--verbose", f"{BASEDIR}/tests", f"--vcr-record={vcr_mode}"]

    if coverage is not None:
        cov = ["coverage", "run", f"--source={SRCDIR}", "-m"]
        cov.extend(pytest)

        exec(cov)
        exec(["coverage", coverage])

    else:
        exec(pytest)


################################################################################
## clean ##


@click.command("cleanup")
@click.option(
    "--clobber",
    "-C",
    default=False,
    is_flag=True,
    help="Remove all generated artifacts.",
)
def cleanup(clobber):
    """Clean intermediate files."""

    if clobber:
        alert("WARNING: this will remove all package artifacts.")
        click.confirm("Do you want to continue?", abort=True)

    info("BEGIN: cleanup")
    debug(f"↳ clobber:{clobber}")

    # rm -f "$(SRCDIR)/*.pyc"
    # rm -f "$(SRCDIR)/examples/*.pyc"

    rmdir(f"{BASEDIR}/__pycache__")
    rmdir(f"{BASEDIR}/tests/__pycache__")
    rmdir(f"{SRCDIR}/notional/__pycache__")

    rmdir(f"{BASEDIR}/build")
    rmdir(f"{BASEDIR}/notional.egg-info")

    os.remove(f"{BASEDIR}/.coverage")

    if clobber:
        exec(["pre-commit", "uninstall"])

        rmdir(f"{BASEDIR}/dist")
        rmdir(f"{BASEDIR}/site")
        rmdir(f"{BASEDIR}/htmlcov")
        rmdir(f"{BASEDIR}/.venv")
