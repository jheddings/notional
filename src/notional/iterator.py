"""Iterator classes for working with paginated API responses."""

import logging
from abc import ABC
from typing import Any, List, Literal, Optional

from pydantic import field_validator

from .blocks import Block, Database, DataRecord, Page
from .core import DataObject, NotionObject, TypedObject
from .user import User

MAX_PAGE_SIZE = 100

logger = logging.getLogger(__name__)


class ObjectList(DataObject, TypedObject, ABC):
    """A paginated list of objects returned by the Notion API."""

    results: List[DataObject] = []
    has_more: bool = False
    next_cursor: Optional[str] = None
    object: Literal["list"] = "list"


#    @field_validator("results", mode="before")
#    def _convert_results_list(cls, val):
#        """Convert the results list to specifc objects."""
#
#        if "object" not in val:
#            raise ValueError("Unknown object in results")
#
#        if val["object"] == PropertyItemList.type:
#            return PropertyItem.deserialize(val)
#
#        return NotionObject.deserialize(val)


class BlockList(ObjectList):
    """A list of Block objects returned by the Notion API."""

    block: Any = {}
    type: Literal["block"] = "block"

    @field_validator("results", mode="before")
    def _convert_results_list(cls, val):
        """Convert the results list to specifc objects."""
        return Block.deserialize(val)


class PageList(ObjectList):
    """A list of Page objects returned by the Notion API."""

    page: Any = {}
    type: Literal["page"] = "page"

    @field_validator("results", mode="before")
    def _convert_results_list(cls, val):
        """Convert the results list to specifc objects."""
        return Page.deserialize(val)


class DatabaseList(ObjectList):
    """A list of Database objects returned by the Notion API."""

    database: Any = {}
    type: Literal["database"] = "database"

    @field_validator("results", mode="before")
    def _convert_results_list(cls, val):
        """Convert the results list to specifc objects."""
        return Database.deserialize(val)


class PageOrDatabaseList(ObjectList):
    """A list of Page or Database objects returned by the Notion API."""

    page_or_database: Any = {}
    type: Literal["page_or_database"] = "page_or_database"

    @field_validator("results", mode="before")
    def _convert_results_list(cls, val):
        """Convert the results list to specifc objects."""
        return DataRecord.deserialize(val)


class UserList(ObjectList):
    """A list of User objects returned by the Notion API."""

    user: Any = {}
    type: Literal["user"] = "user"

    @field_validator("results", mode="before")
    def _convert_results_list(cls, val):
        """Convert the results list to specifc objects."""
        return User.deserialize(val)


class PropertyItemList(ObjectList):
    """A paginated list of property items returned by the Notion API.

    Property item lists contain one or more pages of basic property items.  These types
    do not typically match the schema for corresponding property values.
    """

    class _NestedData(NotionObject):
        id: str
        type: str
        next_url: Optional[str] = None

    property_item: _NestedData
    type: Literal["property_item"] = "property_item"


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

    Objects returned by the iterator may also be converted to a specific type.  This
    is most commonly used to wrap API objects with a higher-level object (such as ORM
    types).
    """

    def __init__(self, endpoint, datatype=None):
        """Initialize an object list iterator for the specified endpoint.

        If a class is provided, it will be constructued for each result returned by
        this iterator.  The constructor must accept a single argument, which is the
        `DataObject` contained in the `ObjectList`.
        """
        self._endpoint = endpoint
        self._datatype = datatype

        self.has_more = None
        self.page_num = -1
        self.total_items = -1
        self.next_cursor = None

    def __call__(self, **kwargs):
        """Return a generator for this endpoint using the given parameters."""

        self.has_more = True
        self.page_num = 0
        self.total_items = 0

        if "page_size" not in kwargs:
            kwargs["page_size"] = MAX_PAGE_SIZE

        self.next_cursor = kwargs.pop("start_cursor", None)

        while self.has_more:
            self.page_num += 1

            page = self._endpoint(start_cursor=self.next_cursor, **kwargs)

            api_list = ObjectList.deserialize(page)

            for obj in api_list.results:
                self.total_items += 1

                if self._datatype is None:
                    yield obj
                else:
                    yield self._datatype(obj)

            self.next_cursor = api_list.next_cursor
            self.has_more = api_list.has_more and self.next_cursor is not None

    def list(self, **kwargs):
        """Collect all items from the endpoint as a list."""

        items = []

        for item in self(**kwargs):
            items.append(item)

        return items
