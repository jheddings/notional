"""Unit tests for the Notional ORM classes."""

from uuid import uuid4

import pytest

from notional import blocks, types
from notional.orm import ConnectedPageBase, Property, connected_page


def test_property_type():
    """Confirm that `Property()` returns a `property`."""

    prop = Property("Special", types.Title)
    assert isinstance(prop, property)


def test_invalid_base_class():
    """Verify that we cannot create connected pages from invalid classes."""

    class _MySpecialPage:
        __database__ = "mock_db"

    with pytest.raises(ValueError):
        connected_page(cls=_MySpecialPage)


def test_session_is_none():
    """Verify we raise expected errors when the session is None."""
    CustomPage = connected_page()

    class _EmptyPage(CustomPage):
        __database__ = "mock_db"

    with pytest.raises(ValueError):
        _EmptyPage.create()


def test_empty_page():
    """Verify expected behavior with an empty page."""
    CustomPage = connected_page()

    class _EmptyPage(CustomPage):
        __database__ = "mock_db"

    empty = _EmptyPage()

    assert isinstance(empty, ConnectedPageBase)
    assert empty.id is None

    num_children = 0

    for _ in empty.children:
        num_children += 1

    assert num_children == 0, f"found {num_children} unexpected child(ren) on page"

    with pytest.raises(ValueError):
        empty += blocks.Divider()


def test_nested_page_id():
    """Make sure the page ID comes through."""
    CustomPage = connected_page()

    class _CustomType(CustomPage):
        __database__ = "mock_db"

    page_id = uuid4()

    data = {"id": page_id.hex}

    page = _CustomType.parse_obj(data)
    assert page.id == page_id


def test_basic_object():
    """Define a basic object using ORM properties."""
    CustomPage = connected_page()

    class _CustomType(CustomPage):
        __database__ = "mock_db"

        Name = Property("Name", types.Title)
