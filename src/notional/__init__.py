"""Provide a simple ORM for Notion objects."""

import logging

from .session import AsyncSession, Session
from .version import __version__

logger = logging.getLogger(__name__)

__all__ = ["__version__", "connect", "async_connect"]


def connect(**kwargs):
    """Connect to Notion using the provided integration token."""

    logger.debug("connecting to Notion (sync)...")

    return Session(**kwargs)


def async_connect(**kwargs):
    """Connect to Notion using the provided integration token with an AsyncClient."""

    logger.debug("connecting to Notion (async)...")

    return AsyncSession(**kwargs)
