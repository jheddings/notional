"""Tools that help maintain Notional."""

import os
import subprocess

import click

BASEDIR = os.path.dirname(__file__)
SRCDIR = f"{BASEDIR}/src"

# TODO install pre-commit hooks
# pre-commit install --install-hooks --overwrite


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


def exec(cmd):
    """Execute the given command."""
    subprocess.run(cmd, check=False, shell=False)


################################################################################
## preflight ##


@click.command("preflight")
def preflight():
    """Run all preflight checks."""

    info("BEGIN: preflight")
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
    "--coverage/--no-coverage",
    "-C/",
    default=False,
    is_flag=True,
    help="Generate a coverage report (default: False).",
)
def run_unit_tests(coverage, vcr_mode):
    """Run unit tests."""

    info("BEGIN: utest")
    debug(f"↳ coverage:{coverage} vcr:{vcr_mode}")

    # TODO set VCR mode

    pytest = ["pytest", "--verbose", f"{BASEDIR}/tests", f"--vcr-record={vcr_mode}"]

    # TODO add support for generating HTML reports

    if coverage:
        test_cmd = ["coverage", "run", f"--source={SRCDIR}", "-m"]
        test_cmd.extend(pytest)

        exec(test_cmd)
        exec(["coverage", "report"])

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

    info("BEGIN: cleanup")

    if clobber:
        alert("WARNING: this will remove all package artifacts.")
        click.confirm("Do you want to continue?", abort=True)

    # rm -f "$(SRCDIR)/*.pyc"
    # rm -f "$(SRCDIR)/examples/*.pyc"
    # rm -Rf "$(SRCDIR)/__pycache__"
    # rm -Rf "$(BASEDIR)/tests/__pycache__"
    # rm -f "$(BASEDIR)/.coverage"
    # rm -Rf "$(BASEDIR)/build"
    # rm -Rf "$(BASEDIR)/notional.egg-info"

    if clobber:
        # pre-commit uninstall
        # rm -Rf "$(DISTDIR)"
        # rm -Rf "$(BASEDIR)/site"
        # rm -Rf "$(BASEDIR)/htmlcov"
        # rm -Rf "$(VENVDIR)"
        pass
