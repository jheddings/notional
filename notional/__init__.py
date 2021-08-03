"""Provide a simple ORM for Notion objects."""

from .session import Session

__version__ = "0.0.3"


def connect(auth):
    """Connect to Notion using the provided integration token."""
    return Session(auth=auth)
