import logging
import unittest

from mocks import mock_endpoint

from notional.iterator import EndpointIterator

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


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
