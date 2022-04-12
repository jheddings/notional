"""Unit tests for Notion API endpoints.

These are considered "live" tests, as they will interact directly with the Notion API.

Running these tests requires setting specific environment variables.  If these
variables are not defined, the tests will be skipped.

Required environment variables:
  - `NOTION_AUTH_TOKEN`: the integration token used for testing.
  - `NOTION_TEST_AREA`: a page ID that can be used for testing
"""

import inspect
import logging
import os
import unittest
from datetime import datetime, timezone

import notional
from notional import blocks, records, schema, session, types, user
from notional.orm import Property, connected_page

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class EndpointTestMixin:
    """Unit tests that require a connected session."""

    notion: session.Session
    parent: records.ParentRef

    def setUp(self):
        """Configure resources needed by these tests."""

        auth_token = os.getenv("NOTION_AUTH_TOKEN", None)

        if auth_token is None:
            raise unittest.SkipTest("missing NOTION_AUTH_TOKEN")

        parent_id = os.getenv("NOTION_TEST_AREA", None)

        if parent_id is None:
            raise unittest.SkipTest("missing NOTION_TEST_AREA")

        self.notion = notional.connect(auth=auth_token)
        self.parent = records.PageRef(page_id=parent_id)

        self._temp_blocks = []

    def tearDown(self):
        """Teardown resources created by these tests."""

        for block in self._temp_blocks:
            self.notion.blocks.delete(block)

        self._temp_blocks.clear()

        if self.notion.IsActive:
            self.notion.close()

    def mktitle(self, title):
        """Make a test-friendly title from the given text."""

        text = ""

        # TODO find name of containing test class

        for frame in inspect.stack():
            if frame.function.startswith("test_"):
                text = frame.function
                break

        if title is not None:
            text += " :: " + title

        return text

    def create_temp_page(self, title=None, children=None):
        """Create a temporary page on the server.

        This page will be deleted during teardown of the test.
        """

        title = self.mktitle(title)

        page = self.notion.pages.create(
            parent=self.parent, title=title, children=children
        )

        self._temp_blocks.append(page)

        return page

    def create_temp_db(self, title=None, schema=None):
        """Create a temporary database on the server.

        This database will be deleted during teardown of the test.
        """

        title = self.mktitle(title)

        db = self.notion.databases.create(
            parent=self.parent, title=title, schema=schema
        )

        self._temp_blocks.append(db)

        return db

    def confirm_blocks(self, page, *blocks):
        """Confirm the expected blocks in a given page."""

        num_blocks = 0

        for block in self.iterate_blocks(page):
            expected = blocks[num_blocks]
            self.assertEqual(type(block), type(expected))
            num_blocks += 1

        self.assertEqual(num_blocks, len(blocks))

    def iterate_blocks(self, page, include_children=False):
        """Iterate over all blocks on a page, including children if specified."""

        for block in self.notion.blocks.children.list(parent=page):
            yield block

            if block.has_children and include_children:
                for child in self.iterate_blocks(block):
                    yield child

    def find_block_on_page(self, page, block_id):
        """Find a block on the given page using its ID."""

        for child in self.iterate_blocks(page):
            if child.id == block_id:
                return child

        return None


class SessionTests(EndpointTestMixin, unittest.TestCase):
    """Unit tests for the Session object."""

    def test_active(self):
        """Verify the session reports as active."""
        self.assertTrue(self.notion.IsActive)

        self.notion.close()

        self.assertFalse(self.notion.IsActive)

    def test_ping(self):
        """Verify the session responds to a ping."""
        self.assertTrue(self.notion.ping())


class BlockEndpointTests(EndpointTestMixin, unittest.TestCase):
    """Test live blocks through the Notion API.

    These tests use an assortment of blocks to help increase coverage.  In most cases,
    the block type itself does not matter to accomplish the intent of the test.
    """

    def test_create_empty_block(self):
        """Create an empty block and confirm its contents."""
        para = blocks.Paragraph()
        page = self.create_temp_page(children=[para])

        self.confirm_blocks(page, para)

    def test_create_block(self):
        """Create a basic block and verify content."""
        page = self.create_temp_page()

        para = blocks.Paragraph.from_text("Hello World")
        self.notion.blocks.children.append(page, para)

        found_block = self.find_block_on_page(page, para.id)
        self.assertIsNotNone(found_block)

    def test_delete_block(self):
        """Create a block, then delete it and make sure it is gone."""
        page = self.create_temp_page()

        block = blocks.Code.from_text("test_delete_block")
        self.notion.blocks.children.append(page, block)

        self.notion.blocks.delete(block)

        found_block = self.find_block_on_page(page, block.id)
        self.assertIsNone(found_block)

    def test_restore_block(self):
        """Delete a block, then restore it and make sure it comes back."""
        page = self.create_temp_page()

        block = blocks.Callout.from_text("Reppearing blocks!")
        self.notion.blocks.children.append(page, block)

        self.notion.blocks.delete(block)
        self.notion.blocks.restore(block)

        found_block = self.find_block_on_page(page, block.id)
        self.assertIsNotNone(found_block)
        self.assertIsInstance(found_block, blocks.Callout)

    def test_retrieve_block(self):
        """Retrieve a specific block using its ID."""
        parent_id = self.parent.page_id
        block = self.notion.blocks.retrieve(parent_id)

        self.assertIsNotNone(block)
        self.assertEqual(parent_id, block.id)

        page = self.create_temp_page()

        block = blocks.Divider()
        self.notion.blocks.children.append(page, block)
        div = self.notion.blocks.retrieve(block.id)

        self.assertEqual(block, div)

    def test_update_block(self):
        """Update a block after it has been created."""
        page = self.create_temp_page()

        block = blocks.ToDo.from_text("Important Task")
        self.notion.blocks.children.append(page, block)

        block.to_do.checked = True
        self.notion.blocks.update(block)

        todo = self.notion.blocks.retrieve(block.id)

        self.assertTrue(todo.IsChecked)
        self.assertEqual(block, todo)


class PageEndpointTests(EndpointTestMixin, unittest.TestCase):
    """Test live pages through the Notion API."""

    def test_blank_page(self):
        """Create an empty page in Notion."""
        page = self.create_temp_page()
        new_page = self.notion.pages.retrieve(page_id=page.id)

        self.assertEqual(page.id, new_page.id)
        self.confirm_blocks(page)

        diff = datetime.now(timezone.utc) - new_page.created_time
        self.assertLessEqual(diff.total_seconds(), 60)

    def test_page_parent(self):
        """Verify page parent references."""
        page = self.create_temp_page()

        self.assertEqual(self.parent, page.parent)

    def test_iterate_page_blocks(self):
        """Iterate over all blocks on the test page and its descendants.

        This is mostly to ensure we do not encounter errors when mapping blocks.  To
        make this effective, the test page should include many different block types.
        """

        for _ in self.iterate_blocks(self.parent, include_children=True):
            pass

    def test_restore_page(self):
        """Create / delete / restore a page; then delete it when we are finished.

        This method will pull a fresh copy of the page each time to ensure that the
        metadata is updated properly.
        """

        page = self.create_temp_page()
        self.assertFalse(page.archived)

        self.notion.pages.delete(page)
        deleted = self.notion.pages.retrieve(page.id)
        self.assertTrue(deleted.archived)

        self.notion.pages.restore(page)
        restored = self.notion.pages.retrieve(page.id)
        self.assertFalse(restored.archived)

    def test_page_icon(self):
        """Set a page icon and confirm."""
        page = self.create_temp_page()
        self.assertIsNone(page.icon)

        snowman = types.EmojiObject(emoji="☃️")
        self.notion.pages.set(page, icon=snowman)

        festive = self.notion.pages.retrieve(page.id)
        self.assertEqual(festive.icon, snowman)

    def test_page_cover(self):
        """Set a page cover and confirm."""
        page = self.create_temp_page()
        self.assertIsNone(page.cover)

        loved = types.ExternalFile.from_url(
            "https://raw.githubusercontent.com/jheddings/notional/main/tests/data/loved.jpg"
        )
        self.notion.pages.set(page, cover=loved)

        covered = self.notion.pages.retrieve(page.id)
        self.assertEqual(covered.cover, loved)


class DatabaseEndpointTests(EndpointTestMixin, unittest.TestCase):
    """Unit tests for database access using the Notion API."""

    def test_create_update_schema(self):
        """Create a simple database and update the schema."""
        props = {"Name": schema.Title()}

        db = self.create_temp_db(
            schema=props,
        )

        new_db = self.notion.databases.retrieve(db.id)
        self.assertEqual(len(new_db.properties), 1)

        props["Index"] = schema.Number()

        self.notion.databases.update(
            new_db,
            title="Improved Database",
            schema=props,
        )

        improved_db = self.notion.databases.retrieve(db.id)
        self.assertEqual(improved_db.Title, "Improved Database")

    def test_restore_database(self):
        """Delete a database, then restore it."""
        db = self.create_temp_db(
            schema={
                "Name": schema.Title(),
            },
        )

        self.notion.databases.delete(db)
        deleted = self.notion.databases.retrieve(db.id)
        self.assertTrue(deleted.archived)

        self.notion.databases.restore(deleted)
        restored = self.notion.databases.retrieve(db.id)
        self.assertFalse(restored.archived)


class SearchEndpointTests(EndpointTestMixin, unittest.TestCase):
    """Test searching through the Notion API."""

    def test_simple_search(self):
        """Make sure search returns some results."""

        search = self.notion.search()

        num_results = 0

        for result in search.execute():
            self.assertIsInstance(result, records.Record)
            num_results += 1

        # sanity check to make sure some results came back
        self.assertGreater(num_results, 0)


class UserEndpointTests(EndpointTestMixin, unittest.TestCase):
    """Test user interaction with the Notion API."""

    def test_user_list(self):
        """Confirm that we can list some users."""
        num_users = 0

        for orig in self.notion.users.list():
            dup = self.notion.users.retrieve(orig.id)
            self.assertEqual(orig, dup)
            num_users += 1

        self.assertGreater(num_users, 0)

    def test_me_bot(self):
        """Verify that the current user looks valid."""
        me = self.notion.users.me()

        self.assertIsNotNone(me)
        self.assertIsInstance(me, user.Bot)


class CustomModelTests(EndpointTestMixin, unittest.TestCase):
    """Test custom objects through the Notion API."""

    def test_simple_model(self):
        """Create a simple custom object and verify connectivity."""
        db = self.create_temp_db(
            schema={
                "Name": schema.Title(),
            },
        )

        CustomPage = connected_page(session=self.notion)

        class _BasicObject(CustomPage):
            __database__ = db.id

            Name = Property("Name", types.Title)

        first = _BasicObject.create(Name="First")
        self.assertEqual(first.Name, "First")

        obj = self.notion.pages.retrieve(first.id)
        self.assertEqual(first.Name, obj.Title)

    def test_changing_basic_properties(self):
        """Create a simple custom object and change its data."""
        db = self.create_temp_db(
            schema={
                "Name": schema.Title(),
            },
        )

        CustomPage = connected_page(session=self.notion)

        class _BasicObject(CustomPage):
            __database__ = db.id

            Name = Property("Name", types.Title)

        first = _BasicObject.create(Name="First")

        obj = self.notion.pages.retrieve(first.id)
        self.assertEqual(first.Name, obj.Title)

        first.Name = "Second"

        self.assertEqual(first.Name, "Second")
        self.assertNotEqual(first.Name, obj.Title)

        obj = self.notion.pages.retrieve(first.id)
        self.assertEqual(first.Name, obj.Title)

    def test_simple_model_with_children(self):
        """Verify appending child blocks to custom types."""
        db = self.create_temp_db(
            schema={
                "Name": schema.Title(),
            },
        )

        CustomPage = connected_page(session=self.notion)

        class _StandardObject(CustomPage):
            __database__ = db.id

            Name = Property("Name", types.Title)

        first = _StandardObject.create(Name="First")
        first += blocks.Heading1.from_text("New Business")

        num_children = 0

        for child in first.children:
            self.assertEqual(child.PlainText, "New Business")
            num_children += 1

        self.assertEqual(num_children, 1)
