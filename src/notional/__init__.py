"""Provide a simple ORM for Notion objects."""

import logging

from .session import Session
from .version import __version__

logger = logging.getLogger(__name__)

__all__ = ["__version__", "connect"]


def connect(**kwargs):
    """Connect to Notion using the provided integration token."""

    logger.debug("connecting to Notion...")

    return Session(**kwargs)
