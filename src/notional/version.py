"""Consistent version information for notional."""

import logging
import os

import pkg_resources

log = logging.getLogger(__name__)

__pkgname__ = "notional"

log.debug("loading package distribution")
_pkg_dist = pkg_resources.get_distribution(__pkgname__)

__version__ = _pkg_dist.version

try:

    # if we are running in a local copy, append the repo information
    log.debug("attempting to parse git repo information")

    import git

    # XXX there is probably a better way to do this, but we don't want to inadvertently
    # pick up another repo (e.g. if we are installed in a .venv of another project)
    _srcdir = os.path.dirname(os.path.abspath(__file__))
    _basedir = os.path.abspath(os.path.join(_srcdir, "..", ".."))

    log.debug("version basedir: %s", _basedir)

    try:
        _repo = git.Repo(_basedir)
        _head = _repo.head.commit

        assert not _repo.bare

        log.debug("using repo dir: %s", _repo.git_dir)

        __version__ += "-" + _head.hexsha[:7]

        _branch = _repo.active_branch.name
        log.debug("current git branch: %s", _branch)

        if _branch != "main":
            __version__ += "-" + _branch

        if _repo.is_dirty():
            __version__ += "+"

    except git.InvalidGitRepositoryError:
        pass

except ModuleNotFoundError:
    log.debug("Could not find module")

except Exception:
    log.exception("Unexpected exception while looking for version information.")

log.info("%s-%s", __pkgname__, __version__)
