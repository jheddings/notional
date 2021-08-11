"""Provide a simple ORM for Notion objects."""

from .session import Session
from .version import __version__


def connect(auth):
    """Connect to Notion using the provided integration token."""
    return Session(auth=auth)
