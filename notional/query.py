"""Provides an interactive query builder for Notion databases."""

import logging
from datetime import date, datetime
from enum import Enum
from inspect import isclass
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import Field, validator

from .blocks import Block
from .core import DataObject
from .iterator import EndpointIterator
from .orm import ConnectedPageBase
from .records import Database, Page, Record

log = logging.getLogger(__name__)


def get_target_id(target):
    if isinstance(target, str):
        return target

    elif isinstance(target, UUID):
        return target.hex

    elif isinstance(target, Record):
        return target.id.hex

    elif isclass(target) and issubclass(target, ConnectedPageBase):
        if target._orm_database_id_ is None:
            raise ValueError("ConnectedPage has no database")

        return target._orm_database_id_

    raise ValueError("unsupported query target")


class QueryFilter(DataObject):
    """Base class for query filters."""


class TextConstraint(DataObject):
    """Represents text criteria in Notion."""

    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    contains: Optional[str] = None
    does_not_contain: Optional[str] = None
    starts_with: Optional[str] = None
    ends_with: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class NumberConstraint(DataObject):
    """Represents number criteria in Notion."""

    equals: Optional[Union[float, int]] = None
    does_not_equal: Optional[Union[float, int]] = None
    greater_than: Optional[Union[float, int]] = None
    less_than: Optional[Union[float, int]] = None
    greater_than_or_equal_to: Optional[Union[float, int]] = None
    less_than_or_equal_to: Optional[Union[float, int]] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class CheckboxConstraint(DataObject):
    """Represents checkbox criteria in Notion."""

    equals: Optional[bool] = None
    does_not_equal: Optional[bool] = None


class SelectOneConstraint(DataObject):
    """Represents select criteria in Notion."""

    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class MultiSelectConstraint(DataObject):
    """Represents a multi_select criteria in Notion."""

    contains: Optional[str] = None
    does_not_contains: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class DateConstraint(DataObject):
    """Represents date criteria in Notion."""

    equals: Optional[Union[date, datetime]] = None
    before: Optional[Union[date, datetime]] = None
    after: Optional[Union[date, datetime]] = None
    on_or_before: Optional[Union[date, datetime]] = None
    on_or_after: Optional[Union[date, datetime]] = None

    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None

    past_week: Optional[Any] = None
    past_month: Optional[Any] = None
    past_year: Optional[Any] = None
    next_week: Optional[Any] = None
    next_month: Optional[Any] = None
    next_year: Optional[Any] = None


class PeopleConstraint(DataObject):
    """Represents people criteria in Notion."""

    contains: Optional[UUID] = None
    does_not_contain: Optional[UUID] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class FilesConstraint(DataObject):
    """Represents files criteria in Notion."""

    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class RelationConstraint(DataObject):
    """Represents relation criteria in Notion."""

    contains: Optional[UUID] = None
    does_not_contain: Optional[UUID] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class FormulaConstraint(DataObject):
    """Represents formula criteria in Notion."""

    text: Optional[TextConstraint] = None
    checkbox: Optional[CheckboxConstraint] = None
    number: Optional[NumberConstraint] = None
    date: Optional[DateConstraint] = None


class PropertyFilter(QueryFilter):
    """Represents a database property filter in Notion."""

    property: str

    text: Optional[TextConstraint] = None
    number: Optional[NumberConstraint] = None
    checkbox: Optional[CheckboxConstraint] = None
    select: Optional[SelectOneConstraint] = None
    multi_select: Optional[MultiSelectConstraint] = None
    date: Optional[DateConstraint] = None
    people: Optional[PeopleConstraint] = None
    files: Optional[FilesConstraint] = None
    relation: Optional[RelationConstraint] = None
    formula: Optional[FormulaConstraint] = None


class CompoundFilter(QueryFilter):
    """Represents a compound filter in Notion."""

    class Config:
        allow_population_by_field_name = True

    and_: Optional[List[QueryFilter]] = Field(None, alias="and")
    or_: Optional[List[QueryFilter]] = Field(None, alias="or")


class SortTimestamp(str, Enum):
    """Time sort fields."""

    created_time = "created_time"
    last_edited_time = "last_edited_time"


class SortDirection(str, Enum):
    """Sort direction options."""

    ascending = "ascending"
    descending = "descending"


class PropertySort(DataObject):
    """Represents a sort instruction in Notion."""

    property: Optional[str] = None
    timestamp: Optional[SortTimestamp] = None
    direction: Optional[SortDirection] = None


class Query(DataObject):
    """Represents a query object in Notion."""

    sorts: Optional[List[PropertySort]] = None
    filter: Optional[QueryFilter] = None
    start_cursor: Optional[UUID] = None
    page_size: int = 100

    @validator("page_size")
    def valid_page_size(cls, value):
        assert value > 0, "size must be greater than zero"
        assert value <= 100, "size must be less than or equal to 100"
        return value


class QueryBuilder(object):
    """A query builder for the Notion API.

    :param endpoint: the session endpoint used to execute the query
    :param cls: an optional DataObject class for parsing results
    :param params: optional params that will be passed to the query
    """

    def __init__(self, endpoint, cls=None, **params):
        self.endpoint = endpoint
        self.params = params
        self.cls = cls

        self.query = Query()

    def filter(self, filter=None, **kwargs):
        """Add the given filter to the query."""

        if filter is None:
            filter = PropertyFilter(**kwargs)

        elif not isinstance(filter, QueryFilter):
            raise ValueError("filter must be of type QueryFilter")

        # use CompoundFilter when necessary...

        if self.query.filter is None:
            self.query.filter = filter

        elif isinstance(self.query.filter, CompoundFilter):
            self.query.filter.and_.append(filter)

        else:
            old_filter = self.query.filter
            self.query.filter = CompoundFilter(and_=[old_filter, filter])

        return self

    def sort(self, sort=None, **kwargs):
        """Add the given sort elements to the query."""

        # XXX should this support ORM properties also?
        # e.g. - query.sort(property=Task.Title)
        # but users won't always use ORM for queries...

        if sort is None:
            sort = PropertySort(**kwargs)

        elif not isinstance(filter, PropertySort):
            raise ValueError("sort must be of type PropertySort")

        # use multiple sorts when necessary

        if self.query.sorts is None:
            self.query.sorts = [sort]

        else:
            self.query.sorts.append(sort)

        return self

    def start_at(self, page_id):
        """Set the start cursor to a specific page ID."""

        self.query.start_cursor = page_id

        return self

    def limit(self, page_size):
        """Limit the number of results to the given page size."""

        self.query.page_size = page_size

        return self

    def execute(self):
        """Execute the current query and return an iterator for the results."""

        if self.endpoint is None:
            raise ValueError("cannot execute query; no endpoint provided")

        log.debug("executing query - %s", self.query)

        query = self.query.to_api()

        if self.params:
            query.update(self.params)

        exec = EndpointIterator(endpoint=self.endpoint, **query)

        return ResultSet(exec=exec, cls=self.cls)

    def first(self):
        """Execute the current query and return the first result only."""

        try:
            return next(self.execute())
        except StopIteration:
            log.debug("iterator returned empty result set")

        return None


class ResultSet(object):
    """A result for a specific query."""

    def __init__(self, exec, cls=None):
        self.source = exec
        self.cls = cls

    def __iter__(self):
        return self

    def __next__(self):
        item = next(self.source)

        if self.cls is not None:
            item = self.cls.parse_obj(item)

        elif "object" in item:
            if item["object"] == "page":
                item = Page.parse_obj(item)
            elif item["object"] == "database":
                item = Database.parse_obj(item)
            elif item["object"] == "block":
                item = Block.parse_obj(item)
            else:
                item = Record.parse_obj(item)

        return item
