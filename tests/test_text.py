"""Unit tests for text types in Notional."""

from notional import blocks
from notional.text import Annotations, TextObject, markdown, plain_text


def confirm_block_markdown(cls, plain, md):
    """Make sure the block type returns expected markdown for the given text."""
    block = cls[plain]

    if plain is not None:
        assert block.PlainText == plain

    if md is not None:
        assert block.Markdown == md


def test_empty_blocks():
    """Ensure that empty blocks behave."""
    confirm_block_markdown(blocks.Paragraph, "", "")

    confirm_block_markdown(blocks.Heading1, "", "")
    confirm_block_markdown(blocks.Heading2, "", "")
    confirm_block_markdown(blocks.Heading3, "", "")

    confirm_block_markdown(blocks.Quote, "", "")


def test_empty_text():
    """Verify text formatting for empty text."""

    assert TextObject[None] is None


def test_zero_length_text():
    """Verify text formatting for zero-length text."""
    text = TextObject[""]

    assert plain_text(text) == ""
    assert markdown(text) == ""


def test_plain_text():
    """Verify text formatting for plain text."""
    text = TextObject["hello world"]

    assert plain_text(text) == "hello world"
    assert markdown(text) == "hello world"


def test_basic_links():
    """Verify text formatting for basic links."""
    text = TextObject["Search Me", "https://www.google.com/"]

    assert plain_text(text) == "Search Me"
    assert markdown(text) == "[Search Me](https://www.google.com/)"


def test_bold_text():
    """Verify text formatting for bold words."""
    bold = Annotations(bold=True)
    text = TextObject["be BOLD", None, bold]

    assert plain_text(text) == "be BOLD"
    assert markdown(text) == "*be BOLD*"


def test_emphasis_text():
    """Verify text formatting for italic words."""
    style = Annotations(italic=True)
    text = TextObject["suggestive", None, style]

    assert plain_text(text) == "suggestive"
    assert markdown(text) == "**suggestive**"


def test_bold_italic_text():
    """Verify text formatting for bold & italic words."""
    style = Annotations(bold=True, italic=True)
    text = TextObject["really important", None, style]

    assert plain_text(text) == "really important"
    assert markdown(text) == "***really important***"


def test_underline_text():
    """Verify text formatting for underline words."""
    underline = Annotations(underline=True)
    text = TextObject["non-standard", None, underline]

    assert plain_text(text) == "non-standard"
    assert markdown(text) == "_non-standard_"


def test_strikethrough():
    """Verify text formatting for strikethrough text."""
    strike = Annotations(strikethrough=True)
    text = TextObject["canceled", None, strike]

    assert plain_text(text) == "canceled"
    assert markdown(text) == "~canceled~"


def test_code_word():
    """Verify text formatting for code words."""
    code = Annotations(code=True)
    text = TextObject["keyword", None, code]

    assert plain_text(text) == "keyword"
    assert markdown(text) == "`keyword`"
