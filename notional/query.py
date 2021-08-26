"""Provides an interactive query builder for Notion databases."""

import logging

import notion_client

from .iterator import EndpointIterator
from .orm import ConnectedPageBase

log = logging.getLogger(__name__)

# TODO add support for start_cursor and page_size - the challenge is that we are using
# EndpointIterator for the results, which overrides those parameters for all results


class Query(object):
    """A query builder for the Notion API.

    :param session: an active session with the Notion SDK
    :param target: either a string with the database ID or an ORM class
    """

    def __init__(self, session, target):
        self.session = session
        self.target = target

        self._filter = list()
        self._sort = list()
        self._start = None
        self._limit = None

    def filter(self, *filters):
        """Add the given filter elements to the query."""

        # XXX see notes on sort()...

        self._filter.extend(filters)

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

            if cls._orm_session_ != self.session:
                raise ValueError("ConnectedPage belongs to a different session")

            if cls._orm_database_id_ is None:
                raise ValueError("ConnectedPage has no database")

            params["database_id"] = cls._orm_database_id_

        else:
            raise ValueError("unsupported query target")

        if self._filter and len(self._filter) > 0:
            params["filter"] = self._filter

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
