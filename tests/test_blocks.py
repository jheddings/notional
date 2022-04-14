"""Unit tests for Notional blocks."""

import pytest

from notional import blocks


def test_para_from_api_data():
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


def test_bookmark_from_url():
    """Create a Bookmark block from a URL."""
    bookmark = blocks.Bookmark["http://example.com"]

    assert bookmark.URL == "http://example.com"
    assert bookmark.Markdown == "<http://example.com>"


def test_embed_from_url():
    """Create an Embed block from a URL."""
    embed = blocks.Embed["https://www.bing.com/"]

    assert embed.URL == "https://www.bing.com/"
    assert embed.Markdown == "<https://www.bing.com/>"


def test_append_without_children_support():
    """Confirm that the mixin handles missing children in subclasses."""

    class _NoChildren(blocks.WithChildrenMixin):
        pass

    block = _NoChildren()
    para = blocks.Paragraph()

    with pytest.raises(TypeError):
        block.append(para)


def test_append_none():
    """Ensure we raise an appropriate error when appending None to a block."""
    para = blocks.Paragraph()

    with pytest.raises(ValueError):
        para.append(None)

    with pytest.raises(ValueError):
        para += None


def test_concat_none():
    """Ensure we raise an appropriate error when concatenating None to a text block."""

    para = blocks.Paragraph()

    para.concat()
    assert para.PlainText == ""

    para.concat(None)
    assert para.PlainText == ""
