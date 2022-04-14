"""Unit tests for the Notional ORM classes."""

from uuid import uuid4

import pytest

from notional import blocks, schema, types
from notional.orm import ConnectedPageBase, Property, connected_page


def test_property_type():
    """Confirm that `Property()` returns a `property`."""

    prop = Property("Special", schema.Title())
    assert isinstance(prop, property)


def test_invalid_property_types():
    """Fail when using incorrect Property definitions."""

    with pytest.raises(AttributeError):
        Property("BAD_TYPE", schema.Title)

    with pytest.raises(AttributeError):
        Property("BAD_TYPE", types.Title())

    with pytest.raises(AttributeError):
        Property("BAD_TYPE", "ImaType")


def test_invalid_base_class():
    """Verify that we cannot create connected pages from invalid classes."""

    class _MySpecialPage:
        __database__ = "mock_db"

    with pytest.raises(ValueError):
        connected_page(cls=_MySpecialPage)


def test_session_is_none(local_model):
    """Verify we raise expected errors when the session is None."""

    with pytest.raises(ValueError):
        local_model.create()


def test_empty_page(local_model):
    """Verify expected behavior with an empty page."""
    empty = local_model()

    assert isinstance(empty, ConnectedPageBase)
    assert empty.id is None

    num_children = 0

    for _ in empty.children:
        num_children += 1

    assert num_children == 0, f"found {num_children} unexpected child(ren) on page"

    with pytest.raises(ValueError):
        empty += blocks.Divider()


def test_custom_model_page_id(local_model):
    """Make sure the page ID comes through."""
    page_id = uuid4()

    data = {"id": page_id.hex}

    page = local_model.parse_obj(data)
    assert page.id == page_id
