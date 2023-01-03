"""Unit tests for Notional databases."""

import pytest

from notional import blocks, schema


def test_empty_database():
    """Create a default Database and verify properties."""

    db = blocks.Database()

    assert db.Title is None


@pytest.mark.vcr()
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


@pytest.mark.vcr()
def test_restore_database(notion, blank_db):
    """Delete a database, then restore it."""
    notion.databases.delete(blank_db)
    deleted = notion.databases.retrieve(blank_db.id)
    assert deleted.archived

    notion.databases.restore(deleted)
    restored = notion.databases.retrieve(blank_db.id)
    assert not restored.archived


@pytest.mark.vcr()
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
