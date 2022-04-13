"""Unit tests for text types in Notional."""

from notional import blocks, text


def test_empty_text():
    """Verify formatting for empty text."""
    assert text.TextObject.from_value(None) is None


def test_zero_length_text():
    """Verify formatting for zero-length text."""

    rtf = [
        text.TextObject.from_value(None),
        text.TextObject.from_value(""),
    ]

    assert text.plain_text(*rtf) == ""


def test_plain_text():
    """Verify formatting for plain text."""

    rtf = [
        text.TextObject.from_value("hello world"),
    ]

    assert text.plain_text(*rtf) == "hello world"


def test_basic_links():
    """Verify formatting for basic links."""

    rtf = [
        text.TextObject.from_value("Search Me", href="https://www.google.com/"),
    ]

    assert text.plain_text(*rtf) == "Search Me"
    assert text.markdown(*rtf) == "[Search Me](https://www.google.com/)"


def test_bold_text():
    """Verify formatting for bold words."""

    rtf = [
        text.TextObject.from_value("be BOLD", bold=True),
    ]

    assert text.plain_text(*rtf) == "be BOLD"
    assert str(*rtf) == "*be BOLD*"


def test_emphasis_text():
    """Verify formatting for italic words."""

    rtf = [
        text.TextObject.from_value("this "),
        text.TextObject.from_value("should", italic=True),
        text.TextObject.from_value(" work"),
    ]

    assert text.plain_text(*rtf) == "this should work"
    assert text.markdown(*rtf) == "this **should** work"


def test_bold_italic_text():
    """Verify formatting for bold & italic words."""

    rtf = [
        text.TextObject.from_value("this is "),
        text.TextObject.from_value("really", bold=True, italic=True),
        text.TextObject.from_value(" "),
        text.TextObject.from_value("important", bold=True),
    ]

    assert text.plain_text(*rtf) == "this is really important"
    assert text.markdown(*rtf) == "this is ***really*** *important*"


def test_underline_text():
    """Verify formatting for underline words."""

    rtf = [
        text.TextObject.from_value("underline", underline=True),
        text.TextObject.from_value(" is not standard markdown"),
    ]

    assert text.plain_text(*rtf) == "underline is not standard markdown"
    assert text.markdown(*rtf) == "_underline_ is not standard markdown"


def test_strikethrough():
    """Verify formatting for strikethrough text."""

    rtf = [
        text.TextObject.from_value("canceled", strikethrough=True),
    ]

    assert text.plain_text(*rtf) == "canceled"
    assert text.markdown(*rtf) == "~canceled~"


def test_code_word():
    """Verify formatting for code words."""

    rtf = [
        text.TextObject.from_value("look at this "),
        text.TextObject.from_value("keyword", code=True),
    ]

    assert text.plain_text(*rtf) == "look at this keyword"
    assert text.markdown(*rtf) == "look at this `keyword`"


def test_heading_1():
    """Verify formatting for Heading1 blocks."""
    block = blocks.Heading1.from_text("Introduction")

    assert block.PlainText == "Introduction"
    assert block.Markdown == "# Introduction #"


def test_heading_2():
    """Verify formatting for Heading2 blocks."""
    block = blocks.Heading2.from_text("More Context")

    assert block.PlainText == "More Context"
    assert block.Markdown == "## More Context ##"


def test_heading_3():
    """Verify formatting for Heading3 blocks."""
    block = blocks.Heading3.from_text("Minor Point")

    assert block.PlainText == "Minor Point"
    assert block.Markdown == "### Minor Point ###"


def test_bulleted_list_item():
    """Verify formatting for BulletedListItem blocks."""
    block = blocks.BulletedListItem.from_text("point number one")

    assert block.PlainText == "point number one"
    assert block.Markdown == "- point number one"


def test_numbered_list_item():
    """Verify formatting for NumberedListItem blocks."""
    block = blocks.NumberedListItem.from_text("first priority")

    assert block.PlainText == "first priority"
    assert block.Markdown == "1. first priority"


def test_todo_block():
    """Verify formatting for ToDo blocks."""
    block = blocks.ToDo.from_text("COMPLETED")
    block.to_do.checked = True

    assert block.PlainText == "COMPLETED"
    assert block.Markdown == "- [x] COMPLETED"

    block = blocks.ToDo.from_text("INCOMPLETE")
    block.to_do.checked = False

    assert block.PlainText == "INCOMPLETE"
    assert block.Markdown == "- [ ] INCOMPLETE"


def test_bookmark():
    """Verify formatting for Bookmark blocks."""
    block = blocks.Bookmark.from_url("https://example.com/")

    assert block.Markdown == "<https://example.com/>"


def test_code_block():
    """Verify formatting for Code blocks."""
    code = "import sys\nprint('hello world')\nsys.exit(0)"
    block = blocks.Code.from_text(code)
    block.code.language = text.CodingLanguage.PYTHON

    assert block.Markdown == f"```python\n{code}\n```"
