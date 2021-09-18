"""Provides an interactive query builder for Notion databases."""

import logging

import notion_client

from .iterator import EndpointIterator

log = logging.getLogger(__name__)

# TODO add support for start_cursor and page_size - the challenge is that we are using
# EndpointIterator for the results, which overrides those parameters for all results


class Query(object):
    """A query builder for the Notion API.

    :param session: an active session with the Notion SDK
    :param source: an EndpointIterator for results
    """

    def __init__(self, session, source, cls=None):
        self.session = session
        self.source = source
        self.cls = cls

        self._filter = list()
        self._sort = list()
        self._start = None
        self._limit = None

    def filter(self, *filters):
        """Add the given filter elements to the query."""

        # XXX see notes on sort()...

        if filters is None:
            self._filter = list()
        else:
            self._filter.extend(filters)

        return self

    def sort(self, *sorts):
        """Add the given sort elements to the query."""

        # XXX should this support ORM properties also?
        # e.g. - query.sort(Task.Title, query.ASC)
        # but users won't always use ORM for queries...

        if sorts is None:
            self._sort = list()
        else:
            self._sort.extend(sorts)

        return self

    # def start_at(self, page_id):
    #     """Set the start cursor to a specific page ID."""
    #     self.source["start_cursor"] = page_id
    #     return self

    # def limit(self, page_size):
    #     """Limit the number of results to the given page size."""
    #     self.source["page_size"] = page_size
    #     return self

    def execute(self):
        """Execute the current query and return an iterator for the results."""

        if self._filter and len(self._filter) > 0:
            self.source["filter"] = self._filter

        if self._sort and len(self._sort) > 0:
            self.source["sorts"] = self._sort

        log.debug("executing query - %s", self.source)

        return ResultSet(session=self.session, src=self.source, cls=self.cls)

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
