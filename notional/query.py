"""Provides an interactive query builder for Notion databases."""

import logging
from datetime import date, datetime
from enum import Enum
from inspect import isclass
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import validator

from .core import DataObject
from .iterator import EndpointIterator
from .orm import ConnectedPageBase

log = logging.getLogger(__name__)

# TODO add support for start_cursor and page_size - the challenge is that we are using
# EndpointIterator for the results, which overrides those parameters for all results


def get_target_id(target):
    if isinstance(target, str):
        return target

    elif isinstance(target, UUID):
        return target.hex

    elif issubclass(target, ConnectedPageBase):
        if target._orm_database_id_ is None:
            raise ValueError("ConnectedPage has no database")

        return target._orm_database_id_

    raise ValueError("unsupported query target")


class QueryFilter(DataObject):
    """Base class for query filters."""


class TextCriteria(DataObject):
    """Represents text criteria in Notion."""

    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    contains: Optional[str] = None
    does_not_contain: Optional[str] = None
    starts_with: Optional[str] = None
    ends_with: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class NumberCriteria(DataObject):
    """Represents number criteria in Notion."""

    equals: Optional[Union[float, int]] = None
    does_not_equal: Optional[Union[float, int]] = None
    greater_than: Optional[Union[float, int]] = None
    less_than: Optional[Union[float, int]] = None
    greater_than_or_equal_to: Optional[Union[float, int]] = None
    less_than_or_equal_to: Optional[Union[float, int]] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class CheckboxCriteria(DataObject):
    """Represents checkbox criteria in Notion."""

    equals: Optional[bool] = None
    does_not_equal: Optional[bool] = None


class SelectOneCriteria(DataObject):
    """Represents select criteria in Notion."""

    equals: Optional[str] = None
    does_not_equal: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class MultiSelectCriteria(DataObject):
    """Represents a multi_select criteria in Notion."""

    contains: Optional[str] = None
    does_not_contains: Optional[str] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class DateCriteria(DataObject):
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


class PeopleCriteria(DataObject):
    """Represents people criteria in Notion."""

    contains: Optional[UUID] = None
    does_not_contain: Optional[UUID] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class FilesCriteria(DataObject):
    """Represents files criteria in Notion."""

    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class RelationCriteria(DataObject):
    """Represents relation criteria in Notion."""

    contains: Optional[UUID] = None
    does_not_contain: Optional[UUID] = None
    is_empty: Optional[bool] = None
    is_not_empty: Optional[bool] = None


class FormulaCriteria(DataObject):
    """Represents formula criteria in Notion."""

    text: Optional[TextCriteria] = None
    checkbox: Optional[CheckboxCriteria] = None
    number: Optional[NumberCriteria] = None
    date: Optional[DateCriteria] = None


class PropertyFilter(QueryFilter):
    """Represents a database property filter in Notion."""

    property: str

    text: Optional[TextCriteria] = None
    number: Optional[NumberCriteria] = None
    checkbox: Optional[CheckboxCriteria] = None
    select: Optional[SelectOneCriteria] = None
    multi_select: Optional[MultiSelectCriteria] = None
    date: Optional[DateCriteria] = None
    people: Optional[PeopleCriteria] = None
    files: Optional[FilesCriteria] = None
    relation: Optional[RelationCriteria] = None
    formula: Optional[FormulaCriteria] = None

    def where_text(self, **kwargs):
        """Method to set the text criteria on this PropertyFilter."""
        self.text = TextCriteria(**kwargs)

    def where_number(self, **kwargs):
        """Method to set the number criteria on this PropertyFilter."""
        self.number = NumberCriteria(**kwargs)

    def where_checkbox(self, **kwargs):
        """Method to set the checkbox criteria on this PropertyFilter."""
        self.checkbox = CheckboxCriteria(**kwargs)

    def where_select(self, **kwargs):
        """Method to set the select criteria on this PropertyFilter."""
        self.select = SelectOneCriteria(**kwargs)

    def where_multi_select(self, **kwargs):
        """Method to set the multi_select criteria on this PropertyFilter."""
        self.multi_select = MultiSelectCriteria(**kwargs)

    def where_date(self, **kwargs):
        """Method to set the date criteria on this PropertyFilter."""
        self.date = DateCriteria(**kwargs)

    def where_people(self, **kwargs):
        """Method to set the people criteria on this PropertyFilter."""
        self.people = PeopleCriteria(**kwargs)

    def where_files(self, **kwargs):
        """Method to set the files criteria on this PropertyFilter."""
        self.files = FilesCriteria(**kwargs)

    def where_formula(self, **kwargs):
        """Method to set the formula criteria on this PropertyFilter."""
        self.formula = FormulaCriteria(**kwargs)

    def where_relation(self, **kwargs):
        """Method to set the relation criteria on this PropertyFilter."""
        self.relation = RelationCriteria(**kwargs)


class CompoundFilter(QueryFilter):
    """Represents a compound filter in Notion."""

    # TODO fix reserved keywords in field names...

    and_: Optional[List[QueryFilter]] = None
    or_: Optional[List[QueryFilter]] = None


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

    sorts: Optional[List[PropertySort]] = None
    filter: Optional[QueryFilter] = None
    start_cursor: Optional[UUID] = None
    page_size: int = 100

    @validator("page_size")
    def valid_page_size(cls, value):
        assert value > 0, "size must be greater than zero"
        assert value <= 100, "size must be less than or equal to 100"
        return value

    def where(self, filters):

        # TODO if self._filter is not None, create a compound for both filters
        # if self._filter is already compound, append to its internal list

        self.filter = filters

    def sort_by(self, *sorts):
        """Add the given sort elements to the query."""

        if not self.sorts:
            self.sorts = list()

        self.sorts.extend(sorts)

    def start_at(self, page_id):
        """Set the start cursor to a specific page ID."""

        self.start_cursor = page_id

    def limit(self, count):
        """Limit the number of results to the given count."""

        self.page_size = count


class QueryBuilder(object):
    """A query builder for the Notion API.

    :param session: an active session with the Notion SDK
    :param target: either a string with the database ID or an ORM class
    """

    def __init__(self, session, target):
        self.session = session
        self.target = target

        self._query = Query()

    def filter(self, **kwargs):
        """Add the given filter to the query."""

        filter = PropertyFilter(**kwargs)

        self._query.where(filter)

        return self

    def sort(self, **kwargs):
        """Add the given sort elements to the query."""

        # XXX should this support ORM properties also?
        # e.g. - query.sort(property=Task.Title)
        # but users won't always use ORM for queries...

        sort = PropertySort(**kwargs)

        self._query.sort_by(sort)

        return self

    # def start_at(self, page_id):
    #     """Set the start cursor to a specific page ID."""
    #     self._start = page_id
    #     return self

    # def limit(self, count):
    #     """Limit the number of results to the given count size."""
    #     self._start = page_id
    #     return self

    def execute(self):
        """Execute the current query and return an iterator for the results."""

        params = {
            "endpoint": self.session.databases().query,
            "database_id": get_target_id(self.target),
        }

        cls = None

        if isclass(self.target) and issubclass(self.target, ConnectedPageBase):
            cls = self.target

        data = self._query.dict(exclude_none=True)
        params.update(data)

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
