"""Unit tests for Notional blocks."""

from notional import blocks


def test_h1_from_text():
    """Create a Heading1 block from text."""
    head = blocks.Heading1.from_text("Welcome!")
    assert head.PlainText == "Welcome!"
    assert head.Markdown == "# Welcome! #"


def test_para_from_text():
    """Create a Paragraph block from text."""
    para = blocks.Paragraph.from_text("Lorem ipsum dolor sit amet")
    assert para.PlainText == "Lorem ipsum dolor sit amet"


def test_para_from_dict():
    """Create a Paragraph block from structured data, simulating the Notion API."""

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

    assert para.object == "block"
    assert para.type == "paragraph"
    assert para.PlainText == "Lorem ipsum dolor sit amet"
    assert para.Markdown == "Lorem ipsum dolor sit amet"
    assert not para.has_children


def test_quote_from_text():
    """Create a Quote block from text."""
    quote = blocks.Quote.from_text("Now is the time for all good men...")
    assert quote.PlainText == "Now is the time for all good men..."
    assert quote.Markdown == "> Now is the time for all good men..."


def test_bookmark_from_url():
    """Create a Bookmark block from a URL."""
    bookmark = blocks.Bookmark.from_url("http://www.google.com")
    assert bookmark.URL == "http://www.google.com"


def test_embed_from_url():
    """Create an Embed block from a URL."""
    embed = blocks.Embed.from_url("http://www.google.com")
    assert embed.URL == "http://www.google.com"
