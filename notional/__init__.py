"""Provide a simple ORM for Notion objects."""

from .session import Session


def connect(auth):
    """Connect to Notion using the provided integration token."""
    return Session(auth=auth)
