import logging
import unittest

from notional import blocks, text

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class PlainTextTest(unittest.TestCase):
    """Unit tests for working with plain text."""

    def test_EmptyText(self):
        rtf = text.TextObject.from_value(None)
        self.assertIsNone(rtf)

    def test_ZeroLengthText(self):
        rtf = [
            text.TextObject.from_value(None),
            text.TextObject.from_value(""),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "")

    def test_BasicPlainText(self):
        rtf = [
            text.TextObject.from_value("hello world"),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "hello world")


class LinkedTextTest(unittest.TestCase):
    """Unit tests for working with links."""

    def test_BasicLinks(self):
        rtf = [
            text.TextObject.from_value("Search Me", href="https://www.google.com/"),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "Search Me")

        md = text.markdown(*rtf)
        self.assertEqual(md, "[Search Me](https://www.google.com/)")


class StyledTextTest(unittest.TestCase):
    """Unit tests for working with annotated text."""

    def test_BoldText(self):
        rtf = [
            text.TextObject.from_value("be BOLD", bold=True),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "be BOLD")

        md = str(*rtf)
        self.assertEqual(md, "*be BOLD*")

    def test_EmphasisText(self):
        rtf = [
            text.TextObject.from_value("this "),
            text.TextObject.from_value("should", italic=True),
            text.TextObject.from_value(" work"),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "this should work")

        md = text.markdown(*rtf)
        self.assertEqual(md, "this **should** work")

    def test_BoldItalicText(self):
        rtf = [
            text.TextObject.from_value("this is "),
            text.TextObject.from_value("really", bold=True, italic=True),
            text.TextObject.from_value(" "),
            text.TextObject.from_value("important", bold=True),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "this is really important")

        md = text.markdown(*rtf)
        self.assertEqual(md, "this is ***really*** *important*")

    def test_UnderlineText(self):
        rtf = [
            text.TextObject.from_value("underline", underline=True),
            text.TextObject.from_value(" is not standard markdown"),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "underline is not standard markdown")

        md = text.markdown(*rtf)
        self.assertEqual(md, "_underline_ is not standard markdown")

    def test_Strikethrough(self):
        rtf = [
            text.TextObject.from_value("canceled", strikethrough=True),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "canceled")

        md = text.markdown(*rtf)
        self.assertEqual(md, "~canceled~")

    def test_CodeWordText(self):
        rtf = [
            text.TextObject.from_value("look at this "),
            text.TextObject.from_value("keyword", code=True),
        ]

        plain = text.plain_text(*rtf)
        self.assertEqual(plain, "look at this keyword")

        md = text.markdown(*rtf)
        self.assertEqual(md, "look at this `keyword`")


class BlockFormatTest(unittest.TestCase):
    """Verify markdown for block objects."""

    def test_Heading1(self):
        block = blocks.Heading1.from_text("Introduction")

        self.assertEqual(block.PlainText, "Introduction")
        self.assertEqual(block.Markdown, "# Introduction #")

    def test_Heading2(self):
        block = blocks.Heading2.from_text("More Context")

        self.assertEqual(block.PlainText, "More Context")
        self.assertEqual(block.Markdown, "## More Context ##")

    def test_Heading3(self):
        block = blocks.Heading3.from_text("Minor Point")

        self.assertEqual(block.PlainText, "Minor Point")
        self.assertEqual(block.Markdown, "### Minor Point ###")

    def test_BulletedItemList(self):
        block = blocks.BulletedListItem.from_text("point number one")

        self.assertEqual(block.PlainText, "point number one")
        self.assertEqual(block.Markdown, "- point number one")

    def test_NumberedItemList(self):
        block = blocks.NumberedListItem.from_text("first priority")

        self.assertEqual(block.PlainText, "first priority")
        self.assertEqual(block.Markdown, "1. first priority")

    def test_ToDo(self):
        block = blocks.ToDo.from_text("COMPLETED")
        block.to_do.checked = True

        self.assertEqual(block.PlainText, "COMPLETED")
        self.assertEqual(block.Markdown, "- [x] COMPLETED")

        block = blocks.ToDo.from_text("INCOMPLETE")
        block.to_do.checked = False

        self.assertEqual(block.PlainText, "INCOMPLETE")
        self.assertEqual(block.Markdown, "- [ ] INCOMPLETE")

    def test_Bookmark(self):
        block = blocks.Bookmark.from_url("https://example.com/")

        self.assertEqual(block.Markdown, "<https://example.com/>")

    def test_Code(self):
        code = "import sys\nprint('hello world')\nsys.exit(0)"
        block = blocks.Code.from_text(code)
        block.code.language = text.CodingLanguage.PYTHON

        self.assertEqual(block.Markdown, f"```python\n{code}\n```")
