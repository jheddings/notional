"""Unit tests for Notional blocks."""

import pytest

from notional import blocks


def add_verify(notion, page, block):
    """Add the block to the give page and read it back."""

    notion.blocks.children.append(page, block)
    new_block = notion.blocks.retrieve(block.id)

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
    block = blocks.ToDo["Important Task"]

    notion.blocks.children.append(test_area, block)

    block.to_do.checked = True
    notion.blocks.update(block)

    # get the new block back from the API
    todo = notion.blocks.retrieve(block.id)

    assert todo.IsChecked
    assert block == todo

    notion.blocks.delete(block)


@pytest.mark.vcr()
def test_bookmark_block(notion, test_page):
    """Create and parse Bookmark blocks."""

    bookmark = blocks.Bookmark["http://example.com"]

    assert bookmark.URL == "http://example.com"
    assert bookmark.Markdown == "<http://example.com>"

    add_verify(notion, test_page, bookmark)


@pytest.mark.vcr()
def test_embed_block(notion, test_page):
    """Create and parse Embed blocks."""

    embed = blocks.Embed["https://www.bing.com/"]

    assert embed.URL == "https://www.bing.com/"
    assert embed.Markdown == "<https://www.bing.com/>"

    add_verify(notion, test_page, embed)


@pytest.mark.vcr()
def test_parse_breadcrumb(notion, test_page):
    """Verify that breadcrumb blocks from the API are parsed correctly."""
    breadcrumb = blocks.Breadcrumb()
    add_verify(notion, test_page, breadcrumb)


@pytest.mark.vcr()
def test_parse_callout(notion, test_page):
    """Verify that callout blocks from the API are parsed correctly."""

    callout = blocks.Callout["Attention!", "⚠️"]

    add_verify(notion, test_page, callout)


@pytest.mark.vcr()
def test_parse_toc_block(notion, test_page):
    """Verify that 'table of contents' from the API are parsed correctly."""
    toc = blocks.TableOfContents()
    add_verify(notion, test_page, toc)


@pytest.mark.vcr()
def test_code_block(notion, test_page):
    """Verify that code blocks from the API are parsed correctly."""

    with open(__file__, "r") as fp:
        text = fp.read()

    code = blocks.Code[text]

    assert code.PlainText == text

    add_verify(notion, test_page, code)


@pytest.mark.vcr()
def test_parse_simple_table(notion):
    """Verify that table blocks from the API are parsed correctly."""
    block_id = "c0bdf627b59c4cf685dd4b3dad8d4755"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.Table)


@pytest.mark.vcr()
def test_parse_synced_block(notion):
    """Verify that synced blocks from the API are parsed correctly."""
    orig_block_id = "c4d5ddc629df458ca4b88f33e5d86857"
    sync_block_id = "f8f177e6fd84418f8405b3e57ca91562"

    orig_block = notion.blocks.retrieve(orig_block_id)
    sync_block = notion.blocks.retrieve(sync_block_id)

    assert isinstance(orig_block, blocks.SyncedBlock)
    assert orig_block.IsOriginal

    assert isinstance(sync_block, blocks.SyncedBlock)
    assert not sync_block.IsOriginal
