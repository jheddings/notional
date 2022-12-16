"""Consistent version information for notional."""

import logging
import os

import pkg_resources

logger = logging.getLogger(__name__)

__pkgname__ = "notional"

_pkg_dist = pkg_resources.get_distribution(__pkgname__)

__version__ = _pkg_dist.version

# if we are running in a local copy, append the repo information
try:

    import git

    # XXX there is probably a better way to do this, but we don't want to inadvertently
    # pick up another repo (e.g. if we are installed in a .venv of another project)
    _srcdir = os.path.dirname(os.path.abspath(__file__))
    _basedir = os.path.abspath(os.path.join(_srcdir, "..", ".."))

    try:
        _repo = git.Repo(_basedir)
        _head = _repo.head.commit

        assert not _repo.bare

        __version__ += "-" + _head.hexsha[:7]

        _branch = _repo.active_branch.name

        if _branch != "main":
            __version__ += "-" + _branch

        if _repo.is_dirty():
            __version__ += "+"

    except git.InvalidGitRepositoryError:
        pass

# if python-git is not installed...
except ModuleNotFoundError:
    logger.debug("repository information not available")
    pass

except Exception:
    logger.exception("Unexpected exception while looking for version information.")

logger.info("%s-%s", __pkgname__, __version__)
