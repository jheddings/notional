import logging
import unittest

from notional import blocks

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class Heading1BlockTest(unittest.TestCase):
    """Unit tests for the Heading1 API objects."""

    def test_FromText(self):
        head = blocks.Heading1.from_text("Welcome!")
        self.assertEqual(head.PlainText, "Welcome!")


class ParagraphBlockTest(unittest.TestCase):
    """Unit tests for the Paragraph API objects."""

    def test_FromText(self):
        para = blocks.Paragraph.from_text("Lorem ipsum dolor sit amet")
        self.assertEqual(para.PlainText, "Lorem ipsum dolor sit amet")

    def test_FromDict(self):

        test_data = {
            "type": "paragraph",
            "object": "block",
            "id": "ec41280d-386e-4bcf-8706-f21704cd798b",
            "created_time": "2021-08-04T17:59:00+00:00",
            "last_edited_time": "2021-08-16T17:44:00+00:00",
            "has_children": False,
            "archived": False,
            "paragraph": {
                "text": [
                    {
                        "type": "text",
                        "plain_text": "Lorem ipsum dolor sit amet",
                        "href": None,
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "text": {"content": "Lorem ipsum dolor sit amet", "link": None},
                    }
                ],
            },
        }

        para = blocks.Paragraph(**test_data)
        self.assertEqual(para.object, "block")
        self.assertEqual(para.type, "paragraph")
        self.assertEqual(para.PlainText, "Lorem ipsum dolor sit amet")
        self.assertFalse(para.has_children)


class QuoteBlockTest(unittest.TestCase):
    """Unit tests for the QuoteParagraph API objects."""

    def test_FromText(self):
        quote = blocks.Quote.from_text("Now is the time for all good men...")
        self.assertEqual(quote.PlainText, "Now is the time for all good men...")


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
