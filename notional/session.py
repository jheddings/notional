"""Provides direct access to the Notion API."""

import logging
from inspect import isclass

import notion_client
from httpx import ConnectError
from notion_client.errors import APIResponseError

from .blocks import Block
from .iterator import EndpointIterator
from .orm import ConnectedPageBase
from .query import QueryBuilder, ResultSet, get_target_id
from .records import Database, Page, ParentRef
from .text import TextObject
from .types import Title
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

            The blocks info will be refreshed based on returned data.
            """

            if parent is None or parent.id is None:
                raise ValueError("Missing parent for append")

            children = [block.to_api() for block in blocks if block is not None]

            log.info("Appending %d blocks to %s ...", len(children), parent.id)

            data = self().append(block_id=parent.id.hex, children=children)

            if "results" in data:

                if len(blocks) == len(data["results"]):
                    for idx in range(len(blocks)):
                        block = blocks[idx]
                        result = data["results"][idx]
                        block.refresh(**result)

                else:
                    log.warning("Unable to refresh results; size mismatch")

            else:
                log.warning("Unable to refresh results; not provided")

            return parent

        # https://developers.notion.com/reference/get-block-children
        def list(self, parent):
            """Returns all Blocks contained by the specified parent."""

            blocks = EndpointIterator(endpoint=self().list, block_id=parent.id)

            log.info("Listing blocks for %s...", parent.id)

            return ResultSet(exec=blocks, cls=Block)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.children = BlocksEndpoint.ChildrenEndpoint(*args, **kwargs)

    def __call__(self):
        return self.session.client.blocks

    # https://developers.notion.com/reference/delete-a-block
    def delete(self, block):
        """Delete (archive) the specified Block."""

        log.info("Deleting block :: %s", block.id)

        data = self().delete(block.id.hex)

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

        parent = ParentRef.from_record(parent)

        log.info("Creating database %s - %s", parent, title)

        request = {
            "parent": parent.to_api(),
            "properties": {name: value.to_api() for name, value in schema.items()},
        }

        if isinstance(title, str):
            title = TextObject.from_value(title)

        if isinstance(title, TextObject):
            request["title"] = [title.to_api()]

        elif title is not None:
            raise ValueError("Unrecognized data in 'title'")

        data = self().create(**request)

        return Database.parse_obj(data)

    # https://developers.notion.com/reference/get-databases
    def list(self):
        """Returns an iterator for all Database objects in the integration scope."""

        # XXX DEPRECATED ###

        log.info("Listing known databases...")

        databases = EndpointIterator(endpoint=self().list)
        return ResultSet(exec=databases, cls=Database)

    # https://developers.notion.com/reference/retrieve-a-database
    def retrieve(self, database_id):
        """Returns the Database with the given ID."""

        log.info("Retrieving database :: %s", database_id)

        data = self().retrieve(database_id)

        return Database.parse_obj(data)

    # https://developers.notion.com/reference/update-a-database
    def update(self, database, title=None, **schema):
        """Updates the Database object on the server.

        The database info will be refreshed to the latest version from the server.
        """

        log.info("Updating database info :: ", database.id)

        request = {}

        if title:
            prop = Title.from_value(title)

            if prop:
                request["title"] = title.to_api()
            else:
                raise ValueError("Invalid title")

        if schema:
            request["properties"] = {
                name: value.to_api() for name, value in schema.items()
            }

        if request:
            data = self().update(database.id.hex, **request)
            database = database.refresh(**data)

        return database

    def delete(self, database):
        """Delete (archive) the specified Database."""

        log.info("Deleting database :: %s", database.id)

        return self.session.blocks.delete(database)

    def restore(self, database):
        """Restore (unarchive) the specified Database."""

        log.info("Restoring database :: %s", database.id)

        data = self().update(database.id.hex, archived=False)

        return database.refresh(**data)

    # https://developers.notion.com/reference/post-database-query
    def query(self, target):
        """Initialized a new Query object with the target data class.

        :param target: either a string with the database ID or an ORM class
        """

        log.info("Initializing database query :: {%s}", get_target_id(target))

        database_id = get_target_id(target)

        cls = None

        if isclass(target) and issubclass(target, ConnectedPageBase):
            cls = target

            if cls._orm_session_ != self.session:
                raise ValueError("ConnectedPage belongs to a different session")

        return QueryBuilder(endpoint=self().query, cls=cls, database_id=database_id)


class PagesEndpoint(Endpoint):
    """Notional interface to the API 'pages' endpoint."""

    def __call__(self):
        return self.session.client.pages

    # https://developers.notion.com/reference/post-page
    def create(self, parent, title=None, properties=None, children=None):
        """Adds a page to the given parent (Page or Database)."""

        if parent is None:
            raise ValueError("'parent' must be provided")

        parent = ParentRef.from_record(parent)
        request = {"parent": parent.to_api()}

        # the API requires a properties object, even if empty
        if properties is None:
            properties = {}

        if title is not None:
            properties["title"] = Title.from_value(title)

        request["properties"] = {
            name: prop.to_api() for name, prop in properties.items()
        }

        if children is not None:
            request["children"] = [child.to_api() for child in children]

        log.info("Creating page :: %s => %s", parent, title)

        data = self().create(**request)

        return Page.parse_obj(data)

    def delete(self, page):
        """Delete (archive) the specified Page."""
        return self.set(page, archived=True)

    def restore(self, page):
        """Restore (unarchive) the specified Page."""
        return self.set(page, archived=False)

    # https://developers.notion.com/reference/retrieve-a-page
    def retrieve(self, page_id):
        """Returns the Page with the given ID."""

        log.info("Retrieving page :: %s", page_id)

        data = self().retrieve(page_id)

        return Page.parse_obj(data)

    # https://developers.notion.com/reference/patch-page
    def update(self, page, **properties):
        """Updates the Page object properties on the server.

        If `properties` are provided, only those values will be updated.  If
        `properties` is empty, all page properties will be updated.

        `properties` are specified as `"name"`: `PropertyValue` pairs.

        The page info will be refreshed to the latest version from the server.
        """

        log.info("Updating page info :: %s", page.id)

        if not properties:
            properties = page.properties

        props = {name: value.to_api() for name, value in properties.items()}

        data = self().update(page.id.hex, properties=props)

        return page.refresh(**data)

    def set(self, page, cover=False, icon=False, archived=None):
        """Set specific page attributes (such as cover, icon, etc) on the server.

        To remove an attribute, set its value to None.
        """

        if cover is None:
            log.info("Removing page cover :: %s", page.id)
            data = self().update(page.id.hex, cover={})
        elif cover is not False:
            log.info("Setting page cover :: %s => %s", page.id, cover)
            data = self().update(page.id.hex, cover=cover.to_api())

        if icon is None:
            log.info("Removing page icon :: %s", page.id)
            data = self().update(page.id.hex, icon={})
        elif icon is not False:
            log.info("Setting page icon :: %s => %s", page.id, icon)
            data = self().update(page.id.hex, icon=icon.to_api())

        if archived is False:
            log.info("Restoring page :: %s", page.id)
            data = self().update(page.id.hex, archived=False)
        elif archived is True:
            log.info("Archiving page :: %s", page.id)
            data = self().update(page.id.hex, archived=True)

        return page.refresh(**data)


class SearchEndpoint(Endpoint):
    """Notional interface to the API 'search' endpoint."""

    # https://developers.notion.com/reference/post-search
    def __call__(self, text=None):
        """Performs a search with the optional text."""

        params = {}

        if text is not None:
            params["query"] = text

        return QueryBuilder(endpoint=self.session.client.search, **params)


class UsersEndpoint(Endpoint):
    """Notional interface to the API 'users' endpoint."""

    def __call__(self):
        return self.session.client.users

    # https://developers.notion.com/reference/get-users
    def list(self):
        """Return an iterator for all users in the workspace."""

        users = EndpointIterator(endpoint=self().list)
        log.info("Listing known users...")

        return ResultSet(exec=users, cls=User)

    # https://developers.notion.com/reference/get-user
    def retrieve(self, user_id):
        """Returns the User with the given ID."""

        log.info("Retrieving user :: %s", user_id)

        data = self().retrieve(user_id)

        return User.parse_obj(data)

    # https://developers.notion.com/reference/get-self
    def me(self):
        """Returns the current bot User."""

        log.info("Retrieving current integration bot")

        data = self().me()

        return User.parse_obj(data)


class Session(object):
    """An active session with the Notion SDK."""

    def __init__(self, **kwargs):
        self.client = notion_client.Client(**kwargs)

        self.blocks = BlocksEndpoint(self)
        self.databases = DatabasesEndpoint(self)
        self.pages = PagesEndpoint(self)
        self.search = SearchEndpoint(self)
        self.users = UsersEndpoint(self)

        log.info("Initialized Notion SDK client")

    def ping(self):
        """Confirm that the session is active and able to connect to Notion.

        Raises SessionError if there is a problem, otherwise returns True.
        """

        error = None

        try:

            me = self.users.me()

            if me is None:
                raise SessionError("Unable to get current user")

        except ConnectError:
            error = "Unable to connect to Notion"

        except APIResponseError as err:
            error = str(err)

        if error is not None:
            raise SessionError(error)

        return True
