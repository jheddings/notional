"""Provide a simple ORM for Notion objects."""

import logging

from .session import Session
from .version import __version__

log = logging.getLogger(__name__)


def connect(**kwargs):
    """Connect to Notion using the provided integration token."""

    log.debug("connecting to Notion...")

    return Session(**kwargs)
