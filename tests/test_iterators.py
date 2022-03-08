import logging
import math
import unittest
from random import random

from notional.iterator import EndpointIterator

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


# TODO return bad data / errors from endpoint
def mock_endpoint(item_count, page_size, **params):
    def page_generator(**kwargs):
        page_size = kwargs.get("page_size", 100)
        start = int(kwargs.get("start_cursor", 0))
        user_data = kwargs.get("user_data", None)
        pagenum = math.floor(start / page_size) + 1

        page = [
            {
                "index": x,
                "pagenum": pagenum,
                "content": user_data,
                "data": random(),
            }
            for x in range(start, start + page_size)
            if x < item_count
        ]

        return {
            "next_cursor": str(start + page_size),
            "has_more": (start + len(page) < item_count),
            "results": page,
        }

    return page_generator


class EndpointIteratorTest(unittest.TestCase):
    """Unit tests for the EndpointIterator."""

    def test_BasicUsage(self):
        """Simple test for basic functionality."""

        mock = mock_endpoint(1042, 100)
        iter = EndpointIterator(endpoint=mock, user_data="testing")

        n_items = 0

        for item in iter:
            self.assertEqual(item["index"], n_items)
            self.assertEqual(item["pagenum"], iter.page_number)
            self.assertEqual(item["content"], "testing")

            n_items += 1
            self.assertEqual(iter.total_items, n_items)

        self.assertEqual(n_items, 1042)

    def test_ExactlyOnePage(self):
        """Test the iterator for exactly one page of results."""

        mock = mock_endpoint(100, 100)
        iter = EndpointIterator(endpoint=mock, user_data="one_page")

        n_items = 0

        for item in iter:
            self.assertEqual(item["content"], "one_page")
            self.assertTrue(iter.last_page)
            self.assertEqual(iter.page_number, 1)
            n_items += 1

        self.assertEqual(n_items, 100)

    def test_OneResult(self):
        """Make sure the iterator works for exactly one result."""

        mock = mock_endpoint(1, 100)
        iter = EndpointIterator(endpoint=mock)

        n_items = 0

        for item in iter:
            self.assertIsNone(item["content"])
            self.assertTrue(iter.last_page)
            self.assertEqual(iter.page_number, 1)
            n_items += 1

        self.assertEqual(n_items, 1)

    def test_EmptyResult(self):
        """Make sure the iterator works with empty results."""

        mock = mock_endpoint(0, 100)
        iter = EndpointIterator(endpoint=mock)

        n_items = 0

        for item in iter:
            n_items += 1

        self.assertEqual(n_items, 0)
