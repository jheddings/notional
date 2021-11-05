"""Provides an interactive query builder for Notion databases."""

import logging
from datetime import date, datetime
from typing import Any, List, Optional, Union
from uuid import UUID

import notion_client
from pydantic import BaseModel, validator

from .iterator import EndpointIterator
from .orm import ConnectedPageBase

log = logging.getLogger(__name__)

# TODO add support for start_cursor and page_size - the challenge is that we are using
# EndpointIterator for the results, which overrides those parameters for all results


class TextFilter(BaseModel):
    """Represents a text filter in Notion."""

    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    contains: Optional[str] = None
    does_not_contain: Optional[str] = None
    starts_with: Optional[str] = None
    ends_with: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class NumberFilter(BaseModel):
    """Represents a number filter in Notion."""

    equals: Optional[Union[float, int]] = None
    does_not_equal: Optional[Union[float, int]] = None
    greater_than: Optional[Union[float, int]] = None
    less_than: Optional[Union[float, int]] = None
    greater_than_or_equal_to: Optional[Union[float, int]] = None
    less_than_or_equal_to: Optional[Union[float, int]] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class CheckboxFilter(BaseModel):
    """Represents a checkbox filter in Notion."""

    equals: Optional[bool] = None
    does_not_equal: Optional[bool] = None


class SelectOneFilter(BaseModel):
    """Represents a select filter in Notion."""

    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class MultiSelectFilter(BaseModel):
    """Represents a multi-select filter in Notion."""

    contains: Optional[str] = None
    does_not_contains: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class DateFilter(BaseModel):
    """Represents a date filter in Notion."""

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


class PeopleFilter(BaseModel):
    """Represents a people filter in Notion."""

    contains: Optional[UUID] = None
    does_not_contain: Optional[UUID] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class FilesFilter(BaseModel):
    """Represents a files filter in Notion."""

    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class RelationFilter(BaseModel):
    """Represents a relation filter in Notion."""

    contains: Optional[UUID] = None
    does_not_contain: Optional[UUID] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class FormulaFilter(BaseModel):
    """Represents a formula filter in Notion."""

    text: Optional[TextFilter] = None
    checkbox: Optional[CheckboxFilter] = None
    number: Optional[NumberFilter] = None
    date: Optional[DateFilter] = None


class PropertyFilter(BaseModel):
    """Represents a database property filter in Notion."""

    property: str

    text: Optional[TextFilter] = None
    number: Optional[NumberFilter] = None
    checkbox: Optional[CheckboxFilter] = None
    select: Optional[SelectOneFilter] = None
    multi_select: Optional[MultiSelectFilter] = None
    date: Optional[DateFilter] = None
    people: Optional[PeopleFilter] = None
    files: Optional[FilesFilter] = None
    relation: Optional[RelationFilter] = None
    formula: Optional[FormulaFilter] = None

    @classmethod
    def where_text(cls, **kwargs):
        return cls(text=TextFilter(**kwargs))

    @classmethod
    def where_number(cls, **kwargs):
        return cls(number=NumberFilter(**kwargs))

    @classmethod
    def where_checkbox(cls, **kwargs):
        return cls(checkbox=CheckboxFilter(**kwargs))

    @classmethod
    def where_select(cls, **kwargs):
        return cls(select=SelectOneFilter(**kwargs))

    @classmethod
    def where_multiselect(cls, **kwargs):
        return cls(multi_select=MultiSelectFilter(**kwargs))

    @classmethod
    def where_date(cls, **kwargs):
        return cls(date=DateFilter(**kwargs))

    @classmethod
    def where_people(cls, **kwargs):
        return cls(people=PeopleFilter(**kwargs))

    @classmethod
    def where_files(cls, **kwargs):
        return cls(files=FilesFilter(**kwargs))


class CompoundFilter(BaseModel):
    """Represents a compound filter in Notion."""

    # TODO fix reserved keywords...

    # and: Optional[List[Union[PropertyFilter, CompoundFilter]]] = None
    # or: Optional[List[Union[PropertyFilter, CompoundFilter]]] = None


class Query(object):
    """A query builder for the Notion API.

    :param session: an active session with the Notion SDK
    :param target: either a string with the database ID or an ORM class
    """

    def __init__(self, session, target):
        self.session = session
        self.target = target

        self._filter = None

        self._sort = list()
        self._start = None
        self._limit = None

    def filter(self, filter=None, **kwargs):
        """Add the given filter to the query."""

        # TODO if self._filter is not None, create a compound for both filters
        # if self._filter is already compound, append to the internal list

        if filter:
            self._filter = filter

        elif kwargs:
            filter = PropertyFilter(**kwargs)
            self._filter = filter

        return self

    def sort(self, *sorts):
        """Add the given sort elements to the query."""

        # XXX should this support ORM properties also?
        # e.g. - query.sort(Task.Title, query.ASC)
        # but users won't always use ORM for queries...

        self._sort.extend(sorts)

        return self

    # def start_at(self, page_id):
    #     """Set the start cursor to a specific page ID."""
    #     self._start = page_id
    #     return self

    # def limit(self, page_size):
    #     """Limit the number of results to the given page size."""
    #     self._start = page_id
    #     return self

    def execute(self):
        """Execute the current query and return an iterator for the results."""

        params = {"endpoint": self.session.databases().query}

        cls = None

        if isinstance(self.target, str):
            params["database_id"] = self.target

        elif issubclass(self.target, ConnectedPageBase):
            cls = self.target

            if cls._orm_database_id_ is None:
                raise ValueError("ConnectedPage has no database")

            params["database_id"] = cls._orm_database_id_

        else:
            raise ValueError("unsupported query target")

        if self._filter:
            params["filter"] = self._filter.dict(exclude_none=True)

        if self._sort and len(self._sort) > 0:
            params["sorts"] = self._sort

        if self._start is not None:
            params["start_cursor"] = self._start

        if self._limit is not None:
            params["page_size"] = self._limit

        log.debug("executing query - %s", params)

        # FIXME in order to use start and limit, we need a different
        # mechanism for iterating on results
        items = EndpointIterator(**params)

        return ResultSet(session=self.session, src=items, cls=cls)

    def first(self):
        """Execute the current query and return the first result only."""

        try:
            return next(self.execute())
        except StopIteration:
            log.debug("iterator returned empty result set")

        return None


class ResultSet(object):
    """A result for a specific query."""

    def __init__(self, session, src, cls=None):
        self.session = session
        self.source = src
        self.cls = cls

    def __iter__(self):
        return self

    def __next__(self):
        item = next(self.source)

        if self.cls is not None:
            item = self.cls.parse_obj(item)

        return item
