"""Unit tests for Notional blocks."""

import re

import notion_client
import pytest

from notional import blocks, types
from notional.text import CodingLanguage


def add_verify(notion, page, block):
    """Add the block to the give page and read it back.

    If the assertion fails, the block is left in place for debugging.
    """

    notion.blocks.children.append(page, block)
    new_block = notion.blocks.retrieve(block.id)

    # models are equal if they have the same dict() result
    assert new_block == block

    notion.blocks.delete(block.id)


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
    """Ensure concatenating None to a text block results in empty text."""

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
    block = notion.blocks.delete(block)

    deleted = notion.blocks.retrieve(block.id)

    assert deleted.archived is True
    assert deleted == block


@pytest.mark.vcr()
def test_restore_block(notion, test_area):
    """Delete a block, then restore it and make sure it comes back."""
    block = blocks.Callout["Reappearing blocks!"]

    notion.blocks.children.append(test_area, block)
    deleted = notion.blocks.delete(block)
    assert deleted.archived is True

    # restore and capture the target block
    block = notion.blocks.restore(block)

    # get the new restored back from the API
    restored = notion.blocks.retrieve(block.id)

    assert restored.archived is False
    assert restored == block

    notion.blocks.delete(restored)


@pytest.mark.vcr()
def test_update_block(notion, test_area):
    """Update a block after it has been created."""
    todo = blocks.ToDo["Important Task"]

    notion.blocks.children.append(test_area, todo)

    todo.to_do.checked = True
    notion.blocks.update(todo)

    # get the new block back from the API
    done = notion.blocks.retrieve(todo.id)

    assert done.IsChecked
    assert todo == done

    notion.blocks.delete(todo)


@pytest.mark.vcr()
def test_paragraph(notion, test_page):
    """Verify that paragraph blocks are handled correctly."""

    text = "Lorem ipsum dolor sit amet"
    paragraph = blocks.Paragraph[text]

    assert paragraph.type == "paragraph"

    assert paragraph.PlainText == text
    assert paragraph.Markdown == text

    assert not paragraph.has_children
    assert paragraph.__children__ is None

    add_verify(notion, test_page, paragraph)


@pytest.mark.vcr()
def test_heading_1(notion, test_page):
    """Verify that heading_1 blocks are handled correctly."""
    h1 = blocks.Heading1["Introduction"]

    assert h1.type == "heading_1"

    assert h1.PlainText == "Introduction"
    assert h1.Markdown == "# Introduction #"

    add_verify(notion, test_page, h1)


@pytest.mark.vcr()
def test_heading_2(notion, test_page):
    """Verify that heading_2 blocks are handled correctly."""
    h2 = blocks.Heading2["More Context"]

    assert h2.type == "heading_2"

    assert h2.PlainText == "More Context"
    assert h2.Markdown == "## More Context ##"

    add_verify(notion, test_page, h2)


@pytest.mark.vcr()
def test_heading_3(notion, test_page):
    """Verify that heading_3 blocks are handled correctly."""
    h3 = blocks.Heading3["Minor Point"]

    assert h3.type == "heading_3"

    assert h3.PlainText == "Minor Point"
    assert h3.Markdown == "### Minor Point ###"

    add_verify(notion, test_page, h3)


@pytest.mark.vcr()
def test_bulleted_list_item(notion, test_page):
    """Verify that bulleted_list_item blocks are handled correctly."""
    li = blocks.BulletedListItem["point number one"]

    assert li.type == "bulleted_list_item"

    assert li.PlainText == "point number one"
    assert li.Markdown == "- point number one"

    add_verify(notion, test_page, li)


@pytest.mark.vcr()
def test_numbered_list_item(notion, test_page):
    """Verify that numbered_list_item blocks are handled correctly."""
    li = blocks.NumberedListItem["first priority"]

    assert li.type == "numbered_list_item"

    assert li.PlainText == "first priority"
    assert li.Markdown == "1. first priority"

    add_verify(notion, test_page, li)


@pytest.mark.vcr()
def test_quote(notion, test_page):
    """Verify that quote blocks are handled correctly."""
    quote = blocks.Quote["Now is the time for all good men..."]

    assert quote.type == "quote"

    assert quote.PlainText == "Now is the time for all good men..."
    assert quote.Markdown == "> Now is the time for all good men..."

    add_verify(notion, test_page, quote)


@pytest.mark.vcr()
def test_divider(notion, test_page):
    """Verify that divider blocks are handled correctly."""
    div = blocks.Divider()

    assert div.type == "divider"
    assert re.match(r"^([*_-])\1{2,}$", div.Markdown)

    add_verify(notion, test_page, div)


@pytest.mark.vcr()
def test_todo_incomplete(notion, test_page):
    """Verify that (incomplete) todo blocks are handled correctly."""

    todo = blocks.ToDo["INCOMPLETE", False]

    assert todo.type == "to_do"

    assert todo.PlainText == "INCOMPLETE"
    assert todo.Markdown == "- [ ] INCOMPLETE"

    assert not todo.IsChecked

    add_verify(notion, test_page, todo)


@pytest.mark.vcr()
def test_todo_complete(notion, test_page):
    """Verify that (complete) todo blocks are handled correctly."""

    todo = blocks.ToDo["COMPLETED", True]

    assert todo.type == "to_do"

    assert todo.PlainText == "COMPLETED"
    assert todo.Markdown == "- [x] COMPLETED"

    assert todo.IsChecked

    add_verify(notion, test_page, todo)


@pytest.mark.vcr()
def test_code(notion, test_page):
    """Verify that code blocks are handled correctly."""

    text = "import sys\nprint('hello world')\nsys.exit(0)"
    code = blocks.Code[text, CodingLanguage.PYTHON]

    assert code.PlainText == text
    assert code.Markdown == f"```python\n{text}\n```"

    add_verify(notion, test_page, code)


@pytest.mark.vcr()
def test_bookmark(notion, test_page):
    """Verify that bookmark blocks are handled correctly."""

    bookmark = blocks.Bookmark["http://example.com"]

    assert bookmark.URL == "http://example.com"
    assert bookmark.Markdown == "<http://example.com>"

    add_verify(notion, test_page, bookmark)


@pytest.mark.vcr()
def test_embed(notion, test_page):
    """Verify that embed blocks are handled correctly."""

    embed = blocks.Embed["https://www.bing.com/"]

    assert embed.type == "embed"
    assert embed.URL == "https://www.bing.com/"
    assert embed.Markdown == "<https://www.bing.com/>"

    add_verify(notion, test_page, embed)


@pytest.mark.vcr()
def test_link_preview(notion, test_page):
    """Verify that link_preview blocks are handled correctly."""

    link = blocks.LinkPreview["https://www.youtube.com/"]

    assert link.type == "link_preview"
    assert link.URL == "https://www.youtube.com/"
    assert link.Markdown == "<https://www.youtube.com/>"

    # link_preview blocks cannot be added via the API
    with pytest.raises(notion_client.errors.APIResponseError):
        notion.blocks.children.append(test_page, link)


@pytest.mark.vcr()
def test_breadcrumb(notion, test_page):
    """Verify that breadcrumb blocks are handled correctly."""
    breadcrumb = blocks.Breadcrumb()
    add_verify(notion, test_page, breadcrumb)


@pytest.mark.vcr()
def test_callout(notion, test_page):
    """Verify that callout blocks are handled correctly."""
    callout = blocks.Callout["Attention!", "⚠️"]
    assert callout.type == "callout"
    add_verify(notion, test_page, callout)


@pytest.mark.vcr()
def test_toc(notion, test_page):
    """Verify that table_of_contents are handled correctly."""
    toc = blocks.TableOfContents()
    assert toc.type == "table_of_contents"
    add_verify(notion, test_page, toc)


@pytest.mark.vcr()
def test_image(notion, test_page):
    """Verify that image blocks are handled correctly."""
    img = blocks.Image(
        image=types.ExternalFile[
            "https://raw.githubusercontent.com/jheddings/notional/main/tests/data/loved.png"
        ]
    )
    assert img.type == "image"
    add_verify(notion, test_page, img)


@pytest.mark.vcr()
def test_parse_simple_table(notion):
    """Verify that table blocks from the API are handled correctly."""
    block_id = "c0bdf627b59c4cf685dd4b3dad8d4755"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.Table)


@pytest.mark.vcr()
def test_synced_block(notion):
    """Verify that synced blocks from the API are handled correctly."""
    orig_block_id = "c4d5ddc629df458ca4b88f33e5d86857"
    sync_block_id = "f8f177e6fd84418f8405b3e57ca91562"

    orig_block = notion.blocks.retrieve(orig_block_id)
    sync_block = notion.blocks.retrieve(sync_block_id)

    assert isinstance(orig_block, blocks.SyncedBlock)
    assert orig_block.IsOriginal

    assert isinstance(sync_block, blocks.SyncedBlock)
    assert not sync_block.IsOriginal
