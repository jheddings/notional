"""Consistent version information for notional."""

import logging
import os

import pkg_resources

logger = logging.getLogger(__name__)

__pkgname__ = "notional"

logger.debug("loading package distribution")
_pkg_dist = pkg_resources.get_distribution(__pkgname__)

__version__ = _pkg_dist.version

try:

    # if we are running in a local copy, append the repo information
    logger.debug("attempting to parse git repo information")

    import git

    # XXX there is probably a better way to do this, but we don't want to inadvertently
    # pick up another repo (e.g. if we are installed in a .venv of another project)
    _srcdir = os.path.dirname(os.path.abspath(__file__))
    _basedir = os.path.abspath(os.path.join(_srcdir, "..", ".."))

    logger.debug("version basedir: %s", _basedir)

    try:
        _repo = git.Repo(_basedir)
        _head = _repo.head.commit

        assert not _repo.bare

        logger.debug("using repo dir: %s", _repo.git_dir)

        __version__ += "-" + _head.hexsha[:7]

        _branch = _repo.active_branch.name
        logger.debug("current git branch: %s", _branch)

        if _branch != "main":
            __version__ += "-" + _branch

        if _repo.is_dirty():
            __version__ += "+"

    except git.InvalidGitRepositoryError:
        pass

except ModuleNotFoundError:
    logger.debug("Could not find module")

except Exception:
    logger.exception("Unexpected exception while looking for version information.")

logger.info("%s-%s", __pkgname__, __version__)
