"""Unit tests for the Notional ORM classes."""

import logging
import unittest
from uuid import uuid4

from notional import blocks, types
from notional.orm import ConnectedPageBase, Property, connected_page

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class PropertyTests(unittest.TestCase):
    """Unit tests for working with Property objects."""

    def test_property_type(self):
        """Confirm that `Property()` returns a `property`."""

        prop = Property("Special", types.Title)
        self.assertIsInstance(prop, property)


class ConnectedPageTests(unittest.TestCase):
    """Unit tests for ConnectedPage objects."""

    def test_invalid_base_class(self):
        """Verify that we cannot create connected pages from invalid classes."""

        class _MySpecialPage:
            __database__ = "mock_db"

        with self.assertRaises(ValueError):
            connected_page(cls=_MySpecialPage)

    def test_session_is_none(self):
        """Verify we raise expected errors when the session is None."""
        CustomPage = connected_page()

        class _EmptyPage(CustomPage):
            __database__ = "mock_db"

        with self.assertRaises(ValueError):
            _EmptyPage.create()

    def test_empty_page(self):
        """Verify expected behavior with an empty page."""
        CustomPage = connected_page()

        class _EmptyPage(CustomPage):
            __database__ = "mock_db"

        empty = _EmptyPage()

        self.assertIsInstance(empty, ConnectedPageBase)
        self.assertIsNone(empty.id)

        num_children = 0

        for _ in empty.children:
            num_children += 1

        self.assertEqual(num_children, 0)

        with self.assertRaises(ValueError):
            empty += blocks.Divider()

    def test_nested_page_id(self):
        """Make sure the page ID comes through."""
        CustomPage = connected_page()

        class _CustomType(CustomPage):
            __database__ = "mock_db"

        page_id = uuid4()

        data = {"id": page_id.hex}

        page = _CustomType.parse_obj(data)
        self.assertEqual(page.id, page_id)

    def test_basic_object(self):
        """Define a basic object using ORM properties."""
        CustomPage = connected_page()

        class _CustomType(CustomPage):
            __database__ = "mock_db"

            Name = Property("Name", types.Title)
