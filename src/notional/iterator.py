"""Iterator classes for working with paginated API responses."""

import logging
from abc import ABC, abstractmethod
from typing import Any, List, Optional

from pydantic import BaseModel, validator

from .blocks import Block, Database, Page
from .core import GenericObject, NotionObject, TypedObject
from .types import PropertyItem
from .user import User

MAX_PAGE_SIZE = 100

logger = logging.getLogger(__name__)


class ObjectList(NotionObject, TypedObject, object="list"):
    """A paginated list of objects returned by the Notion API."""

    results: List[NotionObject] = []
    has_more: bool = False
    next_cursor: Optional[str] = None

    @validator("results", pre=True, each_item=True)
    def _convert_results_list(cls, val):
        """Convert the results list to specifc objects."""

        if "object" not in val:
            raise ValueError("Unknown object in results")

        if val["object"] == BlockList.type:
            return Block.parse_obj(val)

        if val["object"] == PageList.type:
            return Page.parse_obj(val)

        if val["object"] == DatabaseList.type:
            return Database.parse_obj(val)

        if val["object"] == PropertyItemList.type:
            return PropertyItem.parse_obj(val)

        if val["object"] == UserList.type:
            return User.parse_obj(val)

        return GenericObject.parse_obj(val)


class BlockList(ObjectList, type="block"):
    """A list of Block objects returned by the Notion API."""

    block: Any = {}


class PageList(ObjectList, type="page"):
    """A list of Page objects returned by the Notion API."""

    page: Any = {}


class DatabaseList(ObjectList, type="database"):
    """A list of Database objects returned by the Notion API."""

    database: Any = {}


class PageOrDatabaseList(ObjectList, type="page_or_database"):
    """A list of Page or Database objects returned by the Notion API."""

    page_or_database: Any = {}


class UserList(ObjectList, type="user"):
    """A list of User objects returned by the Notion API."""

    user: Any = {}


class PropertyItemList(ObjectList, type="property_item"):
    """A paginated list of property items returned by the Notion API.

    Property item lists contain one or more pages of basic property items.  These types
    do not typically match the schema for corresponding property values.
    """

    class _NestedData(GenericObject):
        id: str = None
        type: str = None
        next_url: Optional[str] = None

    property_item: _NestedData = _NestedData()


class ContentIterator(ABC):
    """Base class to handle pagination over arbitrary content."""

    def __init__(self):
        """Initialize the iterator."""

        self.page = None
        self.page_index = -1
        self.page_num = 0
        self.n_items = 0

    def __iter__(self):
        """Initialize the iterator."""
        logger.debug("initializing content iterator")

        return self

    def __next__(self):
        """Return the next item from the result set or raise StopIteration."""
        # load a new page if needed
        if self.page is None or self.page_index >= len(self.page):
            self.page_index = 0
            self.page = self.load_next_page()
            self.page_num += 1

        # if we have run out of results...
        if self.page is None or len(self.page) == 0:
            raise StopIteration

        # pull the next item from the current page
        item = self.page[self.page_index]

        # setup for the next call
        self.page_index += 1
        self.n_items += 1

        return item

    @property
    def page_number(self):
        """Return the current page number of results in this iterator."""
        return self.page_num

    @property
    def total_items(self):
        """Return the total number of items returns by this iterator."""
        return self.n_items

    @abstractmethod
    def load_next_page(self):
        """Retrieve the next page of data as a list of items."""


class PageIterator(ContentIterator, ABC):
    """Base class to handle pagination by page number."""

    def load_next_page(self):
        """Retrieve the next page of data as a list of items."""
        return self.get_page_content(self.page_num + 1)

    @abstractmethod
    def get_page_content(self, page_num):
        """Retrieve the page of data with the given number."""


class PositionalIterator(ContentIterator, ABC):
    """Base class to handle pagination by positional cursor."""

    def __init__(self):
        """Initialize the iterator."""
        super().__init__()
        self.cursor = None
        self.first_pass = True

    def load_next_page(self):
        """Load the next page of data from this iterator."""

        if not self.first_pass and not self.cursor:
            return None

        results = self.get_page_data(self.cursor)

        self.cursor = results.next_cursor
        self.first_pass = False

        return results.items

    @abstractmethod
    def get_page_data(self, cursor):
        """Retrieve the page of data starting at the given cursor."""

    class PageData(BaseModel):
        """Represents a page of data from the Notion API."""

        this_cursor: Optional[Any] = None
        next_cursor: Optional[Any] = None
        items: Optional[List[Any]] = None

        @property
        def page_size(self):
            """Return the page size for this data set."""
            return -1 if self.items is None else len(self.items)


class ResultSetIterator(PositionalIterator, ABC):
    """Base class for iterating over Notion API result sets."""

    def get_page_data(self, cursor):
        """Retrieve the page of data starting at the given cursor."""

        params = {"page_size": MAX_PAGE_SIZE}

        if cursor:
            params["start_cursor"] = cursor

        logger.debug("loading next page - start cursor: %s", cursor)

        # TODO error checking on result
        data = self.load_page_data(params)

        results = PositionalIterator.PageData(
            this_cursor=cursor,
            next_cursor=data["next_cursor"] if data["has_more"] else None,
            items=data["results"] if "results" in data else None,
        )

        logger.debug(
            "loaded %d results; next cursor: %s", results.page_size, results.next_cursor
        )

        return results

    @property
    def last_page(self):
        """Return true if this is the last page of results."""
        return not self.first_pass and self.cursor is None

    @abstractmethod
    def load_page_data(self, params):
        """Load the page of data defined by the given params."""


class LegacyIterator(ResultSetIterator):
    """Base class for iterating over results from an API endpoint."""

    def __init__(self, endpoint, **params):
        """Initialize the `LegacyIterator` for a specific API endpoint.

        :param endpoint: the concrete endpoint to use for this iterator
        :param params: parameters sent to the endpoint when called
        """
        super().__init__()

        self.endpoint = endpoint
        self.params = params or {}

    def __setitem__(self, name, value):
        """Set the parameter in this `LegacyIterator`."""
        self.params[name] = value

    def load_page_data(self, params):
        """Return the next page with given parameters."""
        params.update(self.params)
        return self.endpoint(**params)


class EndpointIterator:
    """Iterates over results from a paginated API response.

    These objects may be reused, however they are not thread safe.  For example,
    after creating the following iterator:

        notion = notional.connect(auth=NOTION_AUTH_TOKEN)
        query = EndpointIterator(notion.databases().query)

    The iterator may be reused with different database ID's:

        for items in query(database_id=first_db):
            ...

        for items in query(database_id=second_db):
            ...
    """

    def __init__(self, endpoint):
        """Initialize an object list iterator."""
        self.endpoint = endpoint

        self.has_mode = None
        self.next_cursor = None
        self.total_items = -1
        self.page_num = -1

    def __call__(self, **kwargs):
        """Return a generator for this endpoint using the given parameters."""

        self.total_items = 0
        self.page_num = 0
        self.has_more = True

        if "page_size" not in kwargs:
            kwargs["page_size"] = MAX_PAGE_SIZE

        self.next_cursor = kwargs.pop("start_cursor", None)

        while self.has_more:
            self.page_num += 1

            page = self.endpoint(start_cursor=self.next_cursor, **kwargs)

            api_list = ObjectList.parse_obj(page)

            for obj in api_list.results:
                self.total_items += 1

                yield obj

            self.next_cursor = api_list.next_cursor
            self.has_more = api_list.has_more and self.next_cursor is not None

    def list(self, **kwargs):
        """Collect all items from the endpoint as a list."""

        all_items = []

        for item in self(**kwargs):
            all_items.append(item)

        return all_items
