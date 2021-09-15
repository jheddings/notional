import json
import logging
import unittest

from notional import blocks

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class Heading1BlockTest(unittest.TestCase):
    """Unit tests for the Heading1 API objects."""

    def test_FromText(self):
        head = blocks.Heading1.from_text("Welcome!")
        # TODO check plain text


class BookmarkBlockTest(unittest.TestCase):
    """Unit tests for the Bookmark API objects."""

    def test_FromURL(self):
        bookmark = blocks.Bookmark.from_url("http://www.google.com")
        self.assertEqual(bookmark.URL, "http://www.google.com")


class EmbedBlockTest(unittest.TestCase):
    """Unit tests for the Embed API objects."""

    def test_FromURL(self):
        embed = blocks.Embed.from_url("http://www.google.com")
        self.assertEqual(embed.URL, "http://www.google.com")
