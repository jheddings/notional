"""Wrapper for Notion API objects."""

import logging

from datetime import datetime

from .types import NativePropertyValue, RichText
from .types import notion_to_python, python_to_notion

from .iterator import EndpointIterator

log = logging.getLogger(__name__)

# TODO support optional 'name' in Attribute and Property (like SQLAlchemy)
# TODO create class generator method and pass client there (like SQLAlchemy)
# TODO make classes thread safe


def Attribute(name, cls=str):
    """Define a data attribute for a Notion Record.

    :param name: the attribute key in the Record
    :param cls: the data type for the property
    """

    log.debug("creating new Attribute: %s", name)

    # TODO make sure we are being called from a Record object

    def fget(self):
        """Return the current value of the attribute."""
        if not isinstance(self, Record):
            raise TypeError("Attributes must be used in a Record object")

        if self._data is None:
            return None

        value = self._data.get(name, None)

        # TODO support type conversion
        return value

    return property(fget)


def Property(name, cls=RichText, default=None):
    """Define a property for a Notion Page object.

    These must be stored in the 'properties' attribute of the Notion data.

    :param name: the Notion table property name
    :param cls: the data type for the property (default = RichText)
    :param default: a default value when creating new objects
    """

    log.debug("creating new Property: %s", name)

    # TODO make sure we are being called from a Page object

    def fget(self):
        """Return the current value of the property as a python object."""
        if not isinstance(self, Page):
            raise TypeError("Properties must be used in a Page object")

        data = self.get_property(name)
        value = notion_to_python(data)

        if value is None:
            return None

        if not isinstance(value, cls):
            raise TypeError(
                f"Type mismatch: expected '{cls}' but found '{type(value)}'"
            )

        # convert native objects to expected types
        if isinstance(value, NativePropertyValue):
            value = value.value

        return value

    def fset(self, value):
        """Set the property to the given value.

        This will invoke the API to update the value on the server.
        """
        if not isinstance(self, Page):
            raise TypeError("Properties must be used in a Page object")

        try:
            data = python_to_notion(value, cls)
        except TypeError:
            raise TypeError(
                f"Type mismatch: expected '{cls}' but found '{type(value)}'"
            )

        # to change the value of a property, we simply need to update the value in the
        # internal data structure...  future calls to fget will "do the right thing"

        self.set_property(name, data)

    return property(fget, fset)


class Record(object):
    """The base type for all API objects."""

    id = Attribute("id")
    object = Attribute("object")
    created_time = Attribute("created_time", cls=datetime)
    last_edited_time = Attribute("last_edited_time", cls=datetime)

    @classmethod
    def __init__(self, session, **data):
        """Initialize the Record object.

        :param session: the active Notion SDK session
        :param data: the raw data from the API for this record
        """
        self._session = session
        self._data = data

    # TODO - update this object from the Notion API
    # def refresh(self):


class Database(Record):
    """A database record type."""

    title = Attribute("title")
    parent = None  # TODO lazy-load reference


class Page(Record):
    """A standard Notion page object."""

    archived = Attribute("archived", cls=bool)
    parent = None  # TODO lazy-load reference

    @classmethod
    def __init__(self, session, **data):
        """Initialize the Record object."""
        super().__init__(session, **data)
        self._pending = dict()

    @classmethod
    def __getitem__(self, key):
        """Indexer for the given property name."""
        prop = self.get_property(key)

        if prop is None:
            raise AttributeError(f"no such property: {key}")

        return prop

    @classmethod
    def __setitem__(self, key, value):
        """Set the object data for the given property."""
        self.set_property(key, value)

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""
        return EndpointIterator(
            endpoint=self._session.blocks.children.list, block_id=self.id
        )

    @classmethod
    def get_property(self, name):
        """Return the raw API data for the given property name."""
        if self._data is None:
            return None

        props = self._data.get("properties", None)
        if props is None:
            return None

        return props.get(name, None)

    @classmethod
    def set_property(self, name, value):
        """Set the raw data for the given property name."""
        if self._data is None:
            self._data = dict()

        props = self._data.get("properties")

        if props is None:
            props = dict()
            self._data["properties"] = props

        prop = props.get(name)

        # TODO we need to reference the page schema here...
        if prop is None:
            prop = dict()
            props[name] = prop

        prop.update(value)

        self._pending[name] = prop

    @classmethod
    def commit(self):
        """Commit any pending changes to this Page object."""
        if self._data is None or len(self._pending) == 0:
            log.debug("no pending changes to commit")
            return

        page_id = self._data["id"]  # FIXME why can't we use self.id here??
        log.info("Committing %d changes to page %s...", len(self._pending), page_id)
        self._session.pages.update(page_id, properties=self._pending)
        self._pending.clear()

    @classmethod
    def append(self, *children):
        page_id = self._data["id"]  # FIXME why can't we use self.id here??
        log.info("Appending %d blocks to page %s...", len(children), page_id)
        return self._session.blocks.children.append(block_id=page_id, children=children)
