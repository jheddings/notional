"""Handle session management with the Notion SDK."""

import logging

import notion_client
from httpx import ConnectError
from notion_client.errors import APIResponseError

from .blocks import Block
from .iterator import EndpointIterator
from .query import Query, ResultSet
from .records import Database, Page, ParentRef
from .types import TextObject, Title
from .user import User

log = logging.getLogger(__name__)

# TODO add support for limits and filters in list() methods...


class SessionError(Exception):
    """Raised when there are issues with the Notion session."""

    def __init__(self, message):
        super().__init__(message)


class Endpoint(object):
    """Notional wrapper for the API endpoints."""

    def __init__(self, session):
        self.session = session


class BlocksEndpoint(Endpoint):
    """Notional interface to the API 'blocks' endpoint."""

    class ChildrenEndpoint(Endpoint):
        """Notional interface to the API 'blocks/children' endpoint."""

        def __call__(self):
            return self.session.client.blocks.children

        # https://developers.notion.com/reference/patch-block-children
        def append(self, parent, *blocks):
            """Adds the given blocks as children of the specified parent.

            The parent info will be refreshed to the latest version from the server.
            """

            children = [block.to_api() for block in blocks if block is not None]

            log.info("Appending %d blocks to %s...", len(children), parent.id)

            data = self().append(block_id=parent.id.hex, children=children)

            return parent.refresh(**data)

        # https://developers.notion.com/reference/get-block-children
        def list(self, parent):
            """Returns all Blocks contained by the specified parent."""

            blocks = EndpointIterator(endpoint=self().list, block_id=parent.id)

            log.info("Listing blocks for %s...", parent.id)

            return ResultSet(session=self, src=blocks, cls=Block)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.children = BlocksEndpoint.ChildrenEndpoint(*args, **kwargs)

    def __call__(self):
        return self.session.client.blocks

    # https://developers.notion.com/reference/delete-a-block
    def delete(self, block):
        """Delete (archive) the specified Block."""

        log.info("Deleting block :: %s", block.id)

        data = self().update(block.id.hex, archived=True)

        return block.refresh(**data)

    def restore(self, block):
        """Restore (unarchive) the specified Block."""

        log.info("Restoring block :: %s", block.id)

        data = self().update(block.id.hex, archived=False)

        return block.refresh(**data)

    # https://developers.notion.com/reference/retrieve-a-block
    def retrieve(self, block_id):
        """Returns the Block with the given ID."""

        log.info("Retrieving block :: %s", block_id)

        data = self().retrieve(block_id)

        return Block.parse_obj(data)

    # https://developers.notion.com/reference/update-a-block
    def update(self, block):
        """Update the block content on the server.

        The block info will be refreshed to the latest version from the server.
        """

        log.info("Updating block :: %s", block.id)

        data = self().update(block.id.hex, **block.to_api())

        return block.refresh(**data)


class DatabasesEndpoint(Endpoint):
    """Notional interface to the API 'databases' endpoint."""

    def __call__(self):
        return self.session.client.databases

    # https://developers.notion.com/reference/create-a-database
    def create(self, parent, schema, title=None):
        """Adds a database to the given Page parent."""

        parent_id = get_parent_id(parent)

        log.info("Creating database [%s] - %s", parent_id, title)

        props = {name: prop.to_api() for name, prop in schema.items()}

        if title is not None:
            title = TextObject.from_value(title)

        data = self().create(
            parent=parent_id,
            title=[title.to_api()],
            properties=props,
        )

        return Database.parse_obj(data)

    # https://developers.notion.com/reference/get-databases
    def list(self):
        """Returns an iterator for all Database objects in the integration scope."""

        # XXX DEPRECATED ###

        log.info("Listing known databases...")

        databases = EndpointIterator(endpoint=self().list)
        return ResultSet(session=self, src=databases, cls=Database)

    # https://developers.notion.com/reference/retrieve-a-database
    def retrieve(self, database_id):
        """Returns the Database with the given ID."""

        log.info("Retrieving database :: %s", database_id)

        data = self().retrieve(database_id)

        return Database.parse_obj(data)

    # https://developers.notion.com/reference/update-a-database
    def update(self, database):
        """Updates the Database object on the server.

        The database info will be refreshed to the latest version from the server.
        """

        log.info("Updating database info :: ", database.id)

        data = self().update(database.id.hex, **database.to_api())

        return database.refresh(**data)

    # https://developers.notion.com/reference/post-database-query
    def query(self, target):
        """Initialized a new Query object with the target data class.

        :param target: either a string with the database ID or an ORM class
        """

        log.info("Initializing database query :: %s", target)

        return Query(self.session, target)


class PagesEndpoint(Endpoint):
    """Notional interface to the API 'pages' endpoint."""

    def __call__(self):
        return self.session.client.pages

    # https://developers.notion.com/reference/post-page
    def create(self, parent, title=None, properties=dict(), children=list()):
        """Adds a page to the given parent (Page or Database)."""

        if parent is None:
            raise ValueError("'parent' must be provided")

        parent_id = get_parent_id(parent)

        if title is not None:
            properties["title"] = Title.from_value(title)

        props = {name: prop.to_api() for name, prop in properties.items()}
        childs = [child.to_api() for child in children]

        log.info("Creating page [%s] - %s", parent_id, title)

        data = self().create(parent=parent_id, properties=props, children=childs)

        return Page.parse_obj(data)

    def delete(self, page):
        """Delete (archive) the specified Page."""

        log.info("Deleting page :: %s", page.id)

        data = self().update(page.id.hex, archived=True)

        return page.refresh(**data)

    def restore(self, page):
        """Restore (unarchive) the specified Page."""

        log.info("Restoring page :: %s", page.id)

        data = self().update(page.id.hex, archived=False)

        return page.refresh(**data)

    # https://developers.notion.com/reference/retrieve-a-page
    def retrieve(self, page_id):
        """Returns the Page with the given ID."""

        log.info("Retrieving page :: %s", page_id)

        data = self().retrieve(page_id)

        return Page.parse_obj(data)

    # https://developers.notion.com/reference/patch-page
    def update(self, page, **kwargs):
        """Updates the Page object on the server.

        If `kwargs` are provided, only those fields will be updated.  If `kwargs` is
        empty, the entire page will be updated.

        The page info will be refreshed to the latest version from the server.
        """

        log.info("Updating page info :: %s", page.id)

        diff = kwargs or page.to_api()

        data = self().update(page.id.hex, **diff)

        return page.refresh(**data)


class UsersEndpoint(Endpoint):
    """Notional interface to the API 'users' endpoint."""

    def __call__(self):
        return self.session.client.users

    # https://developers.notion.com/reference/get-users
    def list(self):
        """Return an iterator for all users in the workspace."""

        users = EndpointIterator(endpoint=self().list)
        log.info("Listing known users...")

        return ResultSet(session=self.session, src=users, cls=User)

    # https://developers.notion.com/reference/get-user
    def retrieve(self, user_id):
        """Returns the User with the given ID."""

        log.info("Retrieving user :: ", user_id)

        data = self.users.retrieve(user_id)

        return User.parse_obj(data)


class Session(object):
    """An active session with the Notion SDK."""

    def __init__(self, **kwargs):
        self.client = notion_client.Client(**kwargs)

        self.blocks = BlocksEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.pages = PagesEndpoint(self)
        # self.search = SearchEndpoint(self) ??
        self.users = UsersEndpoint(self)

        log.info("Initialized Notion SDK client")

    def ping(self):
        """Confirm that the session is active and able to connect to Notion.

        Raises SessionError if there is a problem, otherwise returns True.
        """

        error = None

        try:

            # get a quick list of users in the integration as a connectivity check
            # NOTE we use the endpoint directly to bypass the iterator and limit results

            self.users().list(page_size=1)

        except ConnectError as err:
            error = "Unable to connect to Notion"

        except APIResponseError as err:
            error = str(err)

        if error is not None:
            raise SessionError(error)

        return True


def get_parent_id(parent):
    """Return the correct parent ID based on the object type."""

    if isinstance(parent, ParentRef):
        return parent.to_api()
    elif isinstance(parent, Page):
        return {"type": "page_id", "page_id": parent.id.hex}
    elif isinstance(parent, Database):
        return {"type": "database_id", "database_id": parent.id.hex}

    # TODO should we support adding to the workspace?
    raise ValueError("Unrecognized 'parent' attribute")
