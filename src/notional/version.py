"""Consistent version information for notional."""

import importlib.metadata
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def package_version(pkgname):
    """Determine the version of an installed package."""
    return importlib.metadata.version(pkgname)


def extended_version(pkgname):
    """Calculate extended version information for the named package."""
    version = package_version(pkgname)

    # if we are running in a local copy, append the repo information
    try:
        import git

        # the folder containing notional source
        srcdir = Path(__file__).parent.resolve()

        # XXX there is probably a better way to do this, but we don't want to inadvertently
        # pick up another repo (e.g. if we are installed in a .venv of another project)
        basedir = srcdir.parent.parent

        try:
            repo = git.Repo(basedir, search_parent_directories=False)
            head = repo.head.commit

            assert not repo.bare

            version += "-" + head.hexsha[:7]

            branch = repo.active_branch.name

            if branch != "main":
                version += "+" + branch

            if repo.is_dirty():
                version += "*"

        except git.InvalidGitRepositoryError:
            logger.debug("repository information not available")

        except Exception:
            logger.debug("error processing repository")

    # if python-git is not installed...
    except ModuleNotFoundError:
        logger.debug("unable to load git repository")

    return version


__pkgname__ = "notional"
__version__ = extended_version(__pkgname__)

logger.info("%s-%s", __pkgname__, __version__)
