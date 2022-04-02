import logging
import os
import unittest

from notional import blocks, schema, types
from notional.parser import CsvParser, HtmlParser

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)

BASEDIR = os.path.dirname(os.path.abspath(__file__))


class HtmlDocumentTest(unittest.TestCase):
    """Unit tests for the HtmlParser class."""

    def check_single_block(self, html, expected_type, expected_text):
        parser = HtmlParser()
        parser.parse(html)

        self.assertGreaterEqual(len(parser.content), 1)

        block = parser.content[0]

        self.assertIsInstance(block, expected_type)

        if expected_text is not None:
            self.assertEqual(block.PlainText, expected_text)

        return block

    def check_style(self, text, **expected_style):
        current_style = text.annotations

        for attrib in expected_style:
            current_value = getattr(current_style, attrib)
            expected_value = expected_style[attrib]
            self.assertEqual(current_value, expected_value)

    def test_Dormouse(self):
        parser = HtmlParser()

        filename = os.path.join(BASEDIR, "dormouse.html")
        with open(filename, "r") as fp:
            html = fp.read()

        parser.parse(html)

        self.assertEqual(parser.title, "The Dormouse's Story")
        self.assertIsNotNone(parser.content)
        self.assertGreater(len(parser.content), 0)

    def test_BasicTitle(self):
        html = "<html><head><title>Hello World</title></head></html>"

        parser = HtmlParser()
        parser.parse(html)

        self.assertEqual(parser.title, "Hello World")
        self.assertEqual(len(parser.content), 0)

    def test_BasicComment(self):
        html = "<!-- Hide this text -->"

        parser = HtmlParser()
        parser.parse(html)

        self.assertEqual(len(parser.content), 0)

    def test_BasicDivider(self):
        self.check_single_block(
            html="<body><hr></body>",
            expected_type=blocks.Divider,
            expected_text=None,
        )

    def test_BasicHeading1(self):
        self.check_single_block(
            html="<h1>Heading One</h1>",
            expected_type=blocks.Heading1,
            expected_text="Heading One",
        )

    def test_BasicHeading2(self):
        self.check_single_block(
            html="<h2>Heading Two</h2>",
            expected_type=blocks.Heading2,
            expected_text="Heading Two",
        )

    def test_BasicHeading3(self):
        self.check_single_block(
            html="<h3>Heading Three</h3>",
            expected_type=blocks.Heading3,
            expected_text="Heading Three",
        )

    def test_BasicParagraph(self):
        self.check_single_block(
            html="<p>Lorem ipsum dolor sit amet, ...</p>",
            expected_type=blocks.Paragraph,
            expected_text="Lorem ipsum dolor sit amet, ...",
        )

    def test_ExtraWhitespace(self):
        self.check_single_block(
            html="<p> ...\tconsectetur   adipiscing\nelit.  </p>",
            expected_type=blocks.Paragraph,
            expected_text="... consectetur adipiscing elit.",
        )

    def test_NakedText(self):
        self.check_single_block(
            html="Look ma, no tags!",
            expected_type=blocks.Paragraph,
            expected_text="Look ma, no tags!",
        )

    def test_BasicQuote(self):
        self.check_single_block(
            html="<blockquote>To be, or not to be...</blockquote>",
            expected_type=blocks.Quote,
            expected_text="To be, or not to be...",
        )

    def test_BasicPre(self):
        self.check_single_block(
            html="<pre>    ...that is the question</pre>",
            expected_type=blocks.Code,
            expected_text="    ...that is the question",
        )

    def test_ImplicitText(self):
        html = "<body><div>Open Text</div></body>"

        parser = HtmlParser()
        parser.parse(html)

        found_text = False

        for block in parser.content:
            if isinstance(block, blocks.TextBlock):
                self.assertEqual(block.PlainText, "Open Text")
                found_text = True

        self.assertTrue(found_text)

    def test_SimpleStrongText(self):
        block = self.check_single_block(
            html="<b>Strong Text</b>",
            expected_type=blocks.Paragraph,
            expected_text="Strong Text",
        )

        self.assertEqual(len(block.paragraph.text), 1)
        self.check_style(block.paragraph.text[0], bold=True)

    def test_SimpleEmphasisText(self):
        block = self.check_single_block(
            html="<i>Emphasis Text</i>",
            expected_type=blocks.Paragraph,
            expected_text="Emphasis Text",
        )

        self.assertEqual(len(block.paragraph.text), 1)
        self.check_style(block.paragraph.text[0], italic=True)


class CsvDocumentTest(unittest.TestCase):
    """Unit tests for the CsvParser class."""

    def test_BasicDataCheck(self):
        data = """first,last\none,two"""

        parser = CsvParser(header_row=True)
        parser.parse(data)

        self.assertIn("first", parser.schema)
        self.assertIsInstance(parser.schema["first"], schema.Title)

        self.assertIn("last", parser.schema)
        self.assertIsInstance(parser.schema["last"], schema.RichText)

        self.assertEqual(len(parser.content), 1)

        entry = parser.content[0]

        self.assertIn("first", entry)
        self.assertIsInstance(entry["first"], types.Title)
        self.assertEqual(entry["first"].Value, "one")

        self.assertIn("last", entry)
        self.assertIsInstance(entry["last"], types.RichText)
        self.assertEqual(entry["last"].Value, "two")
