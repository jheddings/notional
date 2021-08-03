"""Handle session management with the Notion SDK."""

import logging
import notion_client

from .query import Query

log = logging.getLogger(__name__)


class Session(object):
    """An active session with the Notion SDK."""

    def __init__(self, **kwargs):
        self.client = notion_client.Client(**kwargs)
        self.log = log.getChild("Session")
        self.log.info("Initialized Notion SDK client")

    def query(self, cls):
        """Initialized a new Query object with the target data class."""
        return Query(self, cls)

    def commit(self):
        """Commit any pending changes back to Notion - reserved for future use."""
        raise NotImplemented("nothing to do here (yet)")

    @property
    def databases(self):
        """Direct access to the databases API endpoint."""
        return self.client.databases

    @property
    def users(self):
        """Direct access to the users API endpoint."""
        return self.client.users

    @property
    def pages(self):
        """Direct access to the pages API endpoint."""
        return self.client.pages

    @property
    def blocks(self):
        """Direct access to the blocks API endpoint."""
        return self.client.blocks

    @property
    def search(self):
        """Direct access to the search API endpoint."""
        return self.client.search
