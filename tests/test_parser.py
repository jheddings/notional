import logging
import os
import unittest

from notional import blocks, schema, types
from notional.parser import CsvParser, HtmlParser
from notional.text import plain_text

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

    def check_table_data(self, html, expected):
        parser = HtmlParser()
        parser.parse(html)

        self.assertEqual(len(parser.content), 1)

        table = parser.content[0]

        self.assertIsInstance(table, blocks.Table)

        nested_table = table.table
        self.assertEqual(len(nested_table.children), len(expected))

        for idx in range(len(nested_table.children)):
            parser_row = table.table.children[idx]
            expected_row = expected[idx]

            self.assertIsInstance(parser_row, blocks.TableRow)

            nested_row = parser_row.table_row
            self.assertEqual(len(nested_row.cells), len(expected_row))

            for jdx in range(len(nested_row.cells)):
                parser_cell = nested_row.cells[jdx]
                expected_cell = expected_row[jdx]

                parser_text = plain_text(*parser_cell)
                expected_text = str(expected_cell)

                self.assertEqual(parser_text, expected_text)

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

    def test_BasicBulletedList(self):
        html = "<ul><li>Eenie</li><li>Meenie</li></ul"

        parser = HtmlParser()
        parser.parse(html)

        self.assertEqual(len(parser.content), 2)

        li = parser.content[0]
        self.assertIsInstance(li, blocks.BulletedListItem)
        self.assertEqual(li.PlainText, "Eenie")

        li = parser.content[1]
        self.assertIsInstance(li, blocks.BulletedListItem)
        self.assertEqual(li.PlainText, "Meenie")

    def test_MalformedNestedList(self):
        html = """<ul>
            <li>Outer A</li>
            <li>Outer B</li>
            <ul>
                <li>Inner A</li>
            </ul>
            <li>Outer C</li>
        </ul>"""

        parser = HtmlParser()
        parser.parse(html)

        self.assertEqual(len(parser.content), 3)

        for block in parser.content:
            self.assertIsInstance(block, blocks.BulletedListItem)

        li = parser.content[1]
        self.assertTrue(li.has_children)

        for block in parser.content[1].__nested_data__.children:
            self.assertIsInstance(block, blocks.BulletedListItem)

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

    def test_BasicTableData(self):
        self.check_table_data(
            html="<table><tr><td>Datum</td></tr></table>",
            expected=[["Datum"]],
        )

    def test_EmptyTableCell(self):
        self.check_table_data(
            html="<table><tr><td></td></tr></table>",
            expected=[[""]],
        )

    def test_TableCellWithDiv(self):
        self.check_table_data(
            html="<table><tr><td><div>hidden DATA</div></td></tr></table>",
            expected=[["hidden DATA"]],
        )


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
