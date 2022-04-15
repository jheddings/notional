"""Unit tests for Notion API endpoints.

These are considered "live" tests, as they will interact directly with the Notion API.

Running these tests requires setting specific environment variables.  If these
variables are not defined, the tests will be skipped.

Required environment variables:
  - `NOTION_AUTH_TOKEN`: the integration token used for testing.
  - `NOTION_TEST_AREA`: a page ID that can be used for testing
"""

from notional import blocks, records, schema, types, user

from .utils import mktitle


def iterate_blocks(notion, parent, include_children=False):
    """Iterate over all blocks on a page, including children if specified."""
    for block in notion.blocks.children.list(parent=parent):
        yield block

        if block.has_children and include_children:
            for child in iterate_blocks(notion, block, include_children=True):
                yield child


def find_block_on_page(notion, parent, block_id):
    """Find a block on the given page using its ID."""

    for child in iterate_blocks(notion, parent):
        if child.id == block_id:
            return child

    return None


def confirm_blocks(notion, parent, *blocks):
    """Confirm the expected blocks in a given page."""

    num_blocks = 0

    for block in iterate_blocks(notion, parent):
        expected = blocks[num_blocks]
        assert type(block) == type(expected)
        num_blocks += 1

    assert num_blocks == len(blocks)


def test_active_session(notion):
    """Verify the session reports as active."""
    assert notion.IsActive

    notion.close()
    assert not notion.IsActive


def test_ping_session(notion):
    """Verify the active session responds to a ping."""
    assert notion.ping()


def test_user_list(notion):
    """Confirm that we can list some users."""
    num_users = 0

    for orig in notion.users.list():
        dup = notion.users.retrieve(orig.id)
        assert orig == dup
        num_users += 1

    assert num_users > 0


def test_me_bot(notion):
    """Verify that the current user looks valid."""
    me = notion.users.me()

    assert me is not None
    assert isinstance(me, user.Bot)


def test_simple_search(notion):
    """Make sure search returns some results."""

    search = notion.search()

    num_results = 0

    for result in search.execute():
        assert isinstance(result, records.Record)
        num_results += 1

    # sanity check to make sure some results came back
    assert num_results > 0


def test_create_block(notion, test_area):
    """Create a single block and confirm its contents."""
    block = blocks.Divider()

    notion.blocks.children.append(test_area, block)
    assert block.id is not None
    assert block.archived is False

    new_block = notion.blocks.retrieve(block.id)
    assert new_block == block

    notion.blocks.delete(new_block)


def test_delete_block(notion, test_area):
    """Create a block, then delete it and make sure it is gone."""
    block = blocks.Code["test_delete_block"]

    notion.blocks.children.append(test_area, block)
    notion.blocks.delete(block)

    deleted = notion.blocks.retrieve(block.id)
    assert deleted.archived is True


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


def test_iterate_page_blocks(notion, test_area):
    """Iterate over all blocks on the test page and its descendants.

    This is mostly to ensure we do not encounter errors when mapping blocks.  To
    make this effective, the test page should include many different block types.
    """

    for _ in iterate_blocks(notion, test_area):
        pass


def test_create_empty_page(notion, blank_page):
    """Create an empty page and confirm its contents."""

    new_page = notion.pages.retrieve(blank_page.id)
    assert blank_page == new_page

    num_children = 0

    for _ in notion.blocks.children.list(new_page):
        num_children += 1

    assert num_children == 0, f"found {num_children} unexpected item(s) in result set"


def test_create_simple_page(notion, test_area):
    """Make sure we can create a page with children."""

    children = [
        blocks.Heading1["Welcome to the Matrix"],
        blocks.Divider(),
        blocks.Paragraph["There is no spoon..."],
    ]

    page = notion.pages.create(
        parent=test_area,
        title=mktitle(),
        children=children,
    )

    confirm_blocks(notion, page, *children)

    notion.pages.delete(page)


def test_restore_page(notion, blank_page):
    """Create / delete / restore a page.

    This method will pull a fresh copy of the page each time to ensure that the
    metadata is updated properly.
    """

    assert not blank_page.archived

    notion.pages.delete(blank_page)
    deleted = notion.pages.retrieve(blank_page.id)
    assert deleted.archived

    notion.pages.restore(deleted)
    restored = notion.pages.retrieve(blank_page.id)
    assert not restored.archived


def test_page_icon(notion, blank_page):
    """Set a page icon and confirm."""
    assert blank_page.icon is None

    snowman = types.EmojiObject["☃️"]
    notion.pages.set(blank_page, icon=snowman)

    winter = notion.pages.retrieve(blank_page.id)
    assert winter.icon == snowman


def test_page_cover(notion, blank_page):
    """Set a page cover and confirm."""
    assert blank_page.cover is None

    loved = types.ExternalFile[
        "https://raw.githubusercontent.com/jheddings/notional/main/tests/data/loved.jpg"
    ]
    notion.pages.set(blank_page, cover=loved)

    covered = notion.pages.retrieve(blank_page.id)
    assert covered.cover == loved


def test_create_database(notion, blank_db):
    """Create a database and confirm its contents."""

    # make sure the schema has exactly 1 entry
    assert len(blank_db.properties) == 1

    new_db = notion.databases.retrieve(blank_db.id)
    assert blank_db == new_db

    num_children = 0

    for _ in notion.blocks.children.list(new_db):
        num_children += 1

    assert num_children == 0, f"found {num_children} unexpected item(s) in result set"


def test_restore_database(notion, blank_db):
    """Delete a database, then restore it."""
    notion.databases.delete(blank_db)
    deleted = notion.databases.retrieve(blank_db.id)
    assert deleted.archived

    notion.databases.restore(deleted)
    restored = notion.databases.retrieve(blank_db.id)
    assert not restored.archived


def test_update_schema(notion, blank_db):
    """Create a simple database and update the schema."""

    props = {
        "Name": schema.Title(),
        "Index": schema.Number(),
        "Notes": schema.RichText(),
        "Complete": schema.Checkbox(),
        "Due Date": schema.Date(),
        "Tags": schema.MultiSelect(),
    }

    notion.databases.update(
        blank_db,
        title="Improved Database",
        schema=props,
    )

    improved_db = notion.databases.retrieve(blank_db.id)

    assert improved_db.Title == "Improved Database"
    assert len(improved_db.properties) == len(props)


def test_simple_model(notion, simple_model):
    """Create a simple object and verify connectivity."""

    only = simple_model.create(Name="One&Only")
    assert only.Name == "One&Only"

    obj = notion.pages.retrieve(only.id)
    assert only.Name == obj.Title


def test_change_model_title(notion, simple_model):
    """Create a simple custom object and change its data."""
    first = simple_model.create(Name="First")

    first.Name = "Second"
    assert first.Name == "Second"

    # in our model, `Name` is the title property...
    obj = notion.pages.retrieve(first.id)
    assert first.Name == obj.Title


def test_simple_model_with_children(simple_model):
    """Verify appending child blocks to custom types."""
    first = simple_model.create(Name="First")
    first += blocks.Heading1["New Business"]

    num_children = 0

    for child in first.children:
        assert child.PlainText == "New Business"
        num_children += 1

    assert num_children == 1
