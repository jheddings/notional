"""Provides an interactive query builder for Notion databases."""

import logging
import notion_client

from .iterator import EndpointIterator

log = logging.getLogger(__name__)

# TODO add support for start_cursor and page_size - the challenge is that we are using
# EndpointIterator for the results, which overrides those parameters for all results


class Query(object):
    """A query builder for the Notion API."""

    def __init__(self, session, database_id, cls=None):
        self.session = session
        self.database = database_id

        self._class = cls
        self._filter = list()
        self._sort = list()
        self._start = None
        self._limit = None

    def filter(self, filters):
        """Add the given filter elements to the query."""
        self._filter.extend(filters)
        return self

    def sort(self, sorts):
        """Add the given sort elements to the query."""
        self._sort.extend(sorts)
        return self

    # def start_at(self, page_id):
    #    """Set the start cursor to a specific page ID."""
    #    self._start = page_id
    #    return self

    # def limit(self, page_size):
    #    """Limit the number of results to the given page size."""
    #    self._start = page_id
    #    return self

    def execute(self):
        """Execute the current query and return an iterator for the results."""
        params = {
            "endpoint": self.session.databases.query,
            "database_id": self.database,
        }

        if self._filter and len(self._filter) > 0:
            params["filter"] = self._filter

        if self._sort and len(self._sort) > 0:
            params["sorts"] = self._sort

        # if self._start is not None:
        #    params["start_cursor"] = self._start

        # if self._limit is not None:
        #    params["page_size"] = self._limit

        # TODO support returning the custom class type
        return EndpointIterator(**params)

    def first(self):
        """Execute the current query and return the first result only."""
        return next(self.execute())
