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


@pytest.mark.vcr()
def test_create_block(notion, test_area):
    """Create a single block and confirm its contents."""
    block = blocks.Divider()

    notion.blocks.children.append(test_area, block)
    assert block.id is not None
    assert block.archived is False

    new_block = notion.blocks.retrieve(block.id)
    assert new_block == block

    notion.blocks.delete(new_block)


@pytest.mark.vcr()
def test_delete_block(notion, test_area):
    """Create a block, then delete it and make sure it is gone."""
    block = blocks.Code["test_delete_block"]

    notion.blocks.children.append(test_area, block)
    notion.blocks.delete(block)

    deleted = notion.blocks.retrieve(block.id)
    assert deleted.archived is True


@pytest.mark.vcr()
def test_restore_block(notion, test_area):
    """Delete a block, then restore it and make sure it comes back."""
    block = blocks.Callout["Reppearing blocks!"]

    notion.blocks.children.append(test_area, block)
    notion.blocks.delete(block)
    notion.blocks.restore(block)

    restored = notion.blocks.retrieve(block.id)

    assert restored.archived is False
    assert restored == block

    notion.blocks.delete(restored)


@pytest.mark.vcr()
def test_update_block(notion, test_area):
    """Update a block after it has been created."""
    block = blocks.ToDo["Important Task"]

    notion.blocks.children.append(test_area, block)

    block.to_do.checked = True
    notion.blocks.update(block)

    todo = notion.blocks.retrieve(block.id)

    assert todo.IsChecked
    assert block == todo

    notion.blocks.delete(block)
