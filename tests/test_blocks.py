"""Unit tests for Notional blocks."""

import pytest

from notional import blocks


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
def test_parse_breadcrumb(notion):
    """Verify that breadcrumb blocks from the API are parsed correctly."""
    block_id = "ebf949622c1a46238fcdc5d7c4fef9bb"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.Breadcrumb)


@pytest.mark.vcr()
def test_parse_callout(notion):
    """Verify that callout blocks from the API are parsed correctly."""
    block_id = "00ade642ce834f6dacb12e2ab0434020"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.Callout)


@pytest.mark.vcr()
def test_parse_toc_block(notion):
    """Verify that 'table of contents' from the API are parsed correctly."""
    block_id = "aadef1ce443c474b9211f196fb2a893c"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.TableOfContents)


@pytest.mark.vcr()
def test_parse_bookmark(notion):
    """Verify that bookmarks from the API are parsed correctly."""
    block_id = "4b6de8fddec5472eb630f328f809944c"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.Bookmark)


@pytest.mark.vcr()
def test_parse_code_block(notion):
    """Verify that code blocks from the API are parsed correctly."""
    block_id = "1872fd9c99b64c14a78053c3bc6c0a7a"

    block = notion.blocks.retrieve(block_id)
    assert isinstance(block, blocks.Code)


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
