"""Provide a simple ORM for Notion objects."""

import logging

from .session import AsyncSession, Session
from .version import __pkgname__, __version__

logger = logging.getLogger(__name__)

__all__ = ["__version__", "__pkgname__", "connect", "aconnect"]


def connect(**kwargs):
    """Connect to Notion using the provided integration token."""

    logger.debug("connecting to Notion (sync)...")

    return Session(**kwargs)


def aconnect(**kwargs):
    """Connect to Notion using the provided integration token with an AsyncClient."""

    logger.debug("connecting to Notion (async)...")

    return AsyncSession(**kwargs)
