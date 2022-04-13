"""Unit tests for text types in Notional."""

import re

from notional import blocks
from notional.text import CodingLanguage, TextObject, markdown, plain_text


def confirm_rtf_markdown(plain, md, rtf):
    """Confirm the expected text for the given list of RichTextObject's."""

    if plain is not None:
        assert plain_text(*rtf) == plain

    if md is not None:
        assert markdown(*rtf) == md


def confirm_block_markdown(cls, plain, md):
    """Make sure the block type returns expected markdown for the given text."""
    block = cls.from_text(plain)

    if plain is not None:
        assert block.PlainText == plain

    if md is not None:
        assert block.Markdown == md


def test_empty_text():
    """Verify text formatting for empty text."""
    assert TextObject.from_value(None) is None


def test_empty_blocks():
    """Ensure that empty blocks behave."""
    confirm_block_markdown(blocks.Paragraph, "", "")

    confirm_block_markdown(blocks.Heading1, "", "")
    confirm_block_markdown(blocks.Heading2, "", "")
    confirm_block_markdown(blocks.Heading3, "", "")

    confirm_block_markdown(blocks.Code, "", "")
    confirm_block_markdown(blocks.Quote, "", "")


def test_zero_length_text():
    """Verify text formatting for zero-length text."""

    confirm_rtf_markdown(
        plain="",
        md="",
        rtf=[
            TextObject.from_value(None),
            TextObject.from_value(""),
        ],
    )


def test_plain_text():
    """Verify text formatting for plain text."""

    confirm_rtf_markdown(
        plain="hello world",
        md="hello world",
        rtf=[
            TextObject.from_value("hello world"),
        ],
    )


def test_basic_links():
    """Verify text formatting for basic links."""

    confirm_rtf_markdown(
        plain="Search Me",
        md="[Search Me](https://www.google.com/)",
        rtf=[
            TextObject.from_value("Search Me", href="https://www.google.com/"),
        ],
    )


def test_bold_text():
    """Verify text formatting for bold words."""

    confirm_rtf_markdown(
        plain="be BOLD",
        md="*be BOLD*",
        rtf=[
            TextObject.from_value("be BOLD", bold=True),
        ],
    )


def test_emphasis_text():
    """Verify text formatting for italic words."""

    confirm_rtf_markdown(
        plain="this should work",
        md="this **should** work",
        rtf=[
            TextObject.from_value("this "),
            TextObject.from_value("should", italic=True),
            TextObject.from_value(" work"),
        ],
    )


def test_bold_italic_text():
    """Verify text formatting for bold & italic words."""

    confirm_rtf_markdown(
        plain="this is really important",
        md="this is ***really*** *important*",
        rtf=[
            TextObject.from_value("this is "),
            TextObject.from_value("really", bold=True, italic=True),
            TextObject.from_value(" "),
            TextObject.from_value("important", bold=True),
        ],
    )


def test_underline_text():
    """Verify text formatting for underline words."""

    confirm_rtf_markdown(
        plain="underline is not standard markdown",
        md="_underline_ is not standard markdown",
        rtf=[
            TextObject.from_value("underline", underline=True),
            TextObject.from_value(" is not standard markdown"),
        ],
    )


def test_strikethrough():
    """Verify text formatting for strikethrough text."""

    confirm_rtf_markdown(
        plain="canceled",
        md="~canceled~",
        rtf=[
            TextObject.from_value("canceled", strikethrough=True),
        ],
    )


def test_code_word():
    """Verify text formatting for code words."""

    confirm_rtf_markdown(
        plain="look at this keyword",
        md="look at this `keyword`",
        rtf=[
            TextObject.from_value("look at this "),
            TextObject.from_value("keyword", code=True),
        ],
    )


def test_paragraph_block():
    """Create a Paragraph block from text."""

    confirm_block_markdown(
        blocks.Paragraph,
        "Lorem ipsum dolor sit amet",
        "Lorem ipsum dolor sit amet",
    )


def test_heading_1():
    """Verify text formatting for Heading1 blocks."""

    confirm_block_markdown(
        blocks.Heading1,
        "Introduction",
        "# Introduction #",
    )


def test_heading_2():
    """Verify text formatting for Heading2 blocks."""

    confirm_block_markdown(
        blocks.Heading2,
        "More Context",
        "## More Context ##",
    )


def test_heading_3():
    """Verify text formatting for Heading3 blocks."""

    confirm_block_markdown(
        blocks.Heading3,
        "Minor Point",
        "### Minor Point ###",
    )


def test_bulleted_list_item():
    """Verify text formatting for BulletedListItem blocks."""

    confirm_block_markdown(
        blocks.BulletedListItem,
        "point number one",
        "- point number one",
    )


def test_numbered_list_item():
    """Verify text formatting for NumberedListItem blocks."""

    confirm_block_markdown(
        blocks.NumberedListItem,
        "first priority",
        "1. first priority",
    )


def test_quote_block():
    """Verify text formatting for Quote blocks."""

    confirm_block_markdown(
        blocks.Quote,
        "Now is the time for all good men...",
        "> Now is the time for all good men...",
    )


def test_divider_block():
    """Create a Divider and check its behavior."""
    div = blocks.Divider()

    assert re.match(r"^([*_-])\1{2,}$", div.Markdown)


def test_todo_block():
    """Verify text formatting for ToDo blocks."""
    block = blocks.ToDo.from_text("COMPLETED")
    block.to_do.checked = True

    assert block.PlainText == "COMPLETED"
    assert block.Markdown == "- [x] COMPLETED"

    block = blocks.ToDo.from_text("INCOMPLETE")
    block.to_do.checked = False

    assert block.PlainText == "INCOMPLETE"
    assert block.Markdown == "- [ ] INCOMPLETE"


def test_code_block():
    """Verify text formatting for Code blocks."""
    code = "import sys\nprint('hello world')\nsys.exit(0)"
    block = blocks.Code.from_text(code)
    block.code.language = CodingLanguage.PYTHON

    assert block.Markdown == f"```python\n{code}\n```"
