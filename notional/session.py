"""Handle session management with the Notion SDK."""

import logging

import notion_client

from .blocks import Block
from .iterator import EndpointIterator
from .query import Query, ResultSet
from .records import Database, Page, ParentRef
from .types import TextObject
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

    def get_page(self, page_id):
        """Returns the Page with the given ID."""

        if page_id is None:
            raise ValueError("'page_id' must be provided")

        data = self.pages.retrieve(page_id)

        return Page.parse_obj(data)

    def add_page(self, parent, title=None):
        """Adds a page to the given parent (Page or Database)."""

        if parent is None:
            raise ValueError("'parent' must be provided")

        parent_id = get_parent_id(parent)

        props = dict()

        if title is not None:
            text = TextObject.from_value(title)
            props["title"] = [text.dict(exclude_none=True)]

        data = self.pages.create(parent=parent_id, properties=props)

        return Page.parse_obj(data)

    def get_database(self, database_id):
        """Returns the Database with the given ID."""

        data = self.databases.retrieve(database_id)
        return Database.parse_obj(data)

    def get_user(self, user_id):
        """Returns the User with the given ID."""

        data = self.users.retrieve(user_id)
        return User.parse_obj(data)

    def get_block(self, block_id):
        """Returns the Block with the given ID."""

        data = self.blocks.retrieve(block_id)
        return Block.parse_obj(data)

    def get_page_blocks(self, page):
        """Returns all Blocks contained on the given Page."""

        blocks = EndpointIterator(endpoint=self.blocks.children.list, block_id=page.id)

        return ResultSet(session=self, src=blocks, cls=Block)

    def add_blocks(self, parent, *blocks):
        """Adds the given blocks as children of the given parent."""

        parent_id = parent.id

        children = [
            block.dict(exclude_none=True) for block in blocks if block is not None
        ]

        return self.blocks.children.append(block_id=parent_id, children=children)

    def query(self, target):
        """Initialized a new Query object with the target data class.

        :param target: either a string with the database ID or an ORM class
        """

        return Query(self, target)

    def save(self, block):
        """Save the block to Notion."""

        if not isinstance(block, Block):
            raise ValueError("'block' must be a subclass of Block")


def get_parent_id(parent):
    """Return the correct parent ID based on the object type."""

    if isinstance(parent, ParentRef):
        return parent.dict()
    elif isinstance(parent, Page):
        return {"type": "page_id", "page_id": parent.id}
    elif isinstance(parent, Database):
        return {"type": "database_id", "database_id": parent.id}

    # TODO should we support adding to the workspace?
    raise ValueError("Unrecognized 'parent' attribute")
