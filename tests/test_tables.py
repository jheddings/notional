"""Unit tests for Notional tables."""

import pytest

from notional import blocks


@pytest.mark.vcr()
def test_create_basic_table(notion, test_area):
    """Test creating a baci table on the test page."""
    table = blocks.Table()

    row1 = blocks.TableRow()
    row1.append("1")
    row1.append("test")
    assert row1.Width == 2

    table.append(row1)
    assert table.Width == 2

    row2 = blocks.TableRow()
    row2.append("2")
    row2.append("")
    assert row2.Width == 2

    table.append(row1)
    assert table.Width == 2

    notion.blocks.children.append(test_area, table)

    new_table = notion.blocks.retrieve(table.id)
    assert new_table.Width == 2

    notion.blocks.delete(table)
