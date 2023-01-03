"""Unit tests for Notional query objects."""

import pytest

from notional import query, types


def test_empty_query():
    """Create an empty query."""
    find = query.QueryBuilder(None)

    with pytest.raises(ValueError):
        find.first()


@pytest.mark.vcr()
def test_basic_number_constraint(notion, simple_db):
    """Filter a query based on a number value."""

    for idx in range(10):
        notion.pages.create(
            parent=simple_db,
            title=f"Item {idx}",
            properties={
                "Index": types.Number[idx],
            },
        )

    find = notion.databases.query(simple_db).filter(
        property="Index", number=query.NumberCondition(equals=7)
    )

    item = find.first()

    assert item["Index"] == 7


@pytest.mark.vcr()
def test_compound_filter(notion, simple_db):
    """Filter a query based on multiple conditions."""

    for idx in range(10):
        notion.pages.create(
            parent=simple_db,
            title=f"Item {idx}",
            properties={
                "Index": types.Number[idx],
            },
        )

    find = (
        notion.databases.query(simple_db)
        .filter(
            property="Index",
            number=query.NumberCondition(greater_than=3),
        )
        .filter(
            property="Index",
            number=query.NumberCondition(less_than_or_equal_to=8),
        )
        .filter(
            property="Name",
            rich_text=query.TextCondition(contains="Item"),
        )
    )

    n_items = 0

    for item in find.execute():
        assert 3 < item["Index"].Value <= 8

        n_items += 1

    assert n_items == 5


def test_invalid_filter():
    """Make sure that bad filters give an error."""
    with pytest.raises(ValueError):
        query.QueryBuilder(None).filter(bad_filter_name="INVALID")


def test_invalid_sort():
    """Make sure that bad sort give an error."""
    with pytest.raises(ValueError):
        query.QueryBuilder(None).sort(sort=False)


@pytest.mark.vcr()
def test_query_database(notion, simple_db):
    """Add an item and query the database."""
    item = notion.pages.create(parent=simple_db, title="Find Me!")
    query = notion.databases.query(simple_db)
    found = query.first()
    assert found == item
