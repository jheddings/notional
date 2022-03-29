import logging
import os
import unittest

from notional import blocks
from notional.parser import HtmlDocumentParser

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)

BASEDIR = os.path.dirname(os.path.abspath(__file__))


class HtmlDocumentTest(unittest.TestCase):
    """Unit tests for the HtmlDocument parser."""

    def test_Dormouse(self):
        parser = HtmlDocumentParser()

        filename = os.path.join(BASEDIR, "dormouse.html")
        with open(filename, "r") as fp:
            html = fp.read()

        parser.parse(html)

        self.assertEqual(parser.title, "The Dormouse's Story")

        self.assertIsNotNone(parser.content)
        self.assertGreater(len(parser.content), 0)

    def test_BasicTitle(self):
        html = """<html><head><title>Hello World</title></head></html>"""

        parser = HtmlDocumentParser()
        parser.parse(html)

        self.assertEqual(parser.title, "Hello World")

    def test_BasicHeading(self):
        html = """<h1>Heading One</h1>\n<h2>Heading Two</h2>\n<h3>Heading Three</h3>"""

        parser = HtmlDocumentParser()
        parser.parse(html)

        heading_one = False
        heading_two = False
        heading_three = False

        for block in parser.content:
            if isinstance(block, blocks.Heading1):
                self.assertEqual(block.PlainText, "Heading One")
                heading_one = True
            elif isinstance(block, blocks.Heading2):
                self.assertEqual(block.PlainText, "Heading Two")
                heading_two = True
            elif isinstance(block, blocks.Heading3):
                self.assertEqual(block.PlainText, "Heading Three")
                heading_three = True
            else:
                self.fail(f"Unexpected block: {block}")

        self.assertTrue(heading_one)
        self.assertTrue(heading_two)
        self.assertTrue(heading_three)
