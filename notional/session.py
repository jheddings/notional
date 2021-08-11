"""Handle session management with the Notion SDK."""

import logging

import notion_client

from .blocks import Database, Page
from .query import Query
from .user import User

log = logging.getLogger(__name__)


class Session(object):
    """An active session with the Notion SDK."""

    def __init__(self, **kwargs):
        self.client = notion_client.Client(**kwargs)
        self.log = log.getChild("Session")
        self.log.info("Initialized Notion SDK client")

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

    def page(self, page_id):
        """Returns the Page with the given ID."""
        data = self.pages.retrieve(page_id)
        return Page.from_json(data)

    def database(self, database_id):
        """Returns the Database with the given ID."""
        data = self.databases.retrieve(database_id)
        return Database.from_json(data)

    def user(self, user_id):
        """Returns the User with the given ID."""
        data = self.users.retrieve(user_id)
        return User.from_json(data)

    def block(self, block_id):
        """Returns the Block with the given ID."""
        data = self.blocks.retrieve(block_id)
        return Block.from_json(data)

    def query(self, target):
        """Initialized a new Query object with the target data class.

        :param target: either a string with the database ID or an ORM class
        """
        return Query(self, target)

    def commit(self):
        """Commit any pending changes back to Notion - reserved for future use."""
        raise NotImplemented("nothing to do here (yet)")
