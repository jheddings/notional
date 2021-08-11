"""Iterator classes for notional."""

import logging
from abc import ABC, abstractmethod

CONTENT_PAGE_SIZE = 100

log = logging.getLogger(__name__)


class ContentIterator(ABC):
    """Base class to handle pagination over content from the Notion API."""

    def __init__(self):
        self.page = None
        self.index = -1
        self.pagenum = 0
        self.log = log.getChild("ContentIterator")

    def __iter__(self):
        """Initialize the iterator."""
        return self

    def __next__(self):
        """Return the next item from the result set or raise StopIteration."""
        # load a new page if needed
        if self.page is None or self.index >= len(self.page):
            self.index = 0
            self.page = self.load_next_page()
            self.pagenum += 1

        # if we have run out of results...
        if self.page is None or len(self.page) == 0:
            raise StopIteration

        # pull the next item from the current page
        item = self.page[self.index]

        # setup for the next call
        self.index += 1

        return item

    @property
    def page_number(self):
        """Return the current page number of results in this iterator."""
        return self.pagenum

    @abstractmethod
    def load_next_page(self):
        # noqa
        pass


class ResultSetIterator(ContentIterator, ABC):
    """Base class for iterating over result sets (using a cursor)."""

    def __init__(self):
        """Initialize the iterator."""
        super().__init__()
        self.cursor = None
        self.log = log.getChild("ResultSetIterator")

    def load_next_page(self):
        """Return the next page of content."""
        if self.cursor is False:
            return None

        params = {"page_size": CONTENT_PAGE_SIZE}

        if self.cursor:
            params["start_cursor"] = self.cursor

        self.log.debug("loading next page - start cursor: %s", self.cursor)

        # TODO error checking on result
        result = self.get_page(params)

        if result["has_more"]:
            self.cursor = result["next_cursor"]
        else:
            self.cursor = False

        results = result["results"]

        self.log.debug("loaded %d results; next cursor: %s", len(results), self.cursor)

        return result["results"]

    @property
    def last_page(self):
        """Return true if this is the last page of results."""
        if self.cursor is None:
            raise ValueError("iterator has not been initialized")

        return self.cursor is False

    @abstractmethod
    def get_page(self, params):
        # noqa
        pass


class EndpointIterator(ResultSetIterator):
    """Base class for iterating over results from an API endpoint."""

    def __init__(self, endpoint, **params):
        super().__init__()
        self.endpoint = endpoint
        self.params = params
        self.log = log.getChild("EndpointIterator")

    def get_page(self, params):
        """Return the next page with given parameters."""
        params.update(self.params)
        return self.endpoint(**params)
