"""Wrapper for Notion API objects."""

import logging

from datetime import datetime

from .types import NativePropertyValue, RichText
from .types import notion_to_python, python_to_notion

from .iterator import EndpointIterator

log = logging.getLogger(__name__)


def Attribute(name, cls=str, default=None):
    """Define a data attribute for a Notion Record.

    :param name: the attribute key in the Record
    :param cls: the data type for the property
    """

    log.debug("creating new Attribute: %s", name)

    def fget(self):
        """Return the current value of the attribute."""
        if not isinstance(self, Record):
            raise TypeError("Attributes must be used in a Record object")

        if self.__data__ is None:
            return None

        value = self.__data__.get(name, None)

        if value is None:
            return default

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

    def fget(self):
        """Return the current value of the property as a python object."""
        if not isinstance(self, Page):
            raise TypeError("Properties must be used in a Page object")

        data = self.get_property(name)
        if data is None:
            return default

        value = notion_to_python(data)

        if not isinstance(value, cls):
            raise TypeError(
                f"Type mismatch: expected '{cls}' but found '{type(value)}'"
            )

        # convert native objects to expected types
        if isinstance(value, NativePropertyValue):
            value = value.value

        return value

    def fset(self, value):
        """Set the property to the given value."""
        if not isinstance(self, Page):
            raise TypeError("Properties must be used in a Page object")

        # TODO only set the value if it has changed from the existing

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

    def __init__(self, session, **data):
        """Initialize the Record object.

        :param session: the active Notion SDK session
        :param data: the raw data from the API for this record
        """
        self._session = session
        self.__data__ = data

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

    def __init__(self, session, **data):
        """Initialize the Record object."""
        super().__init__(session, **data)

        self._pending_props = dict()
        self._pending_children = list()

    def __getitem__(self, key):
        """Indexer for the given property name."""
        data = self.get_property(key)

        if data is None:
            raise AttributeError(f"no such property: {key}")

        return data

    def __setitem__(self, key, data):
        """Set the object data for the given property."""
        self.set_property(key, data)

    def __iadd__(self, child):
        """Append the given child to this Page."""
        self.append(child)

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""
        return EndpointIterator(
            endpoint=self._session.blocks.children.list, block_id=self.id
        )

    def get_property(self, name):
        """Return the raw API data for the given property name."""
        if self.__data__ is None:
            return None

        props = self.__data__.get("properties", None)
        if props is None:
            return None

        return props.get(name, None)

    def set_property(self, name, value):
        """Set the raw data for the given property name."""
        if self.__data__ is None:
            self.__data__ = dict()

        log.debug("set property :: {%s} %s => %s", self.id, name, value)

        props = self.__data__.get("properties")

        if props is None:
            props = dict()
            self.__data__["properties"] = props

        prop = props.get(name)

        # TODO we should reference the page schema here...
        if prop is None:
            prop = dict()
            props[name] = prop

        prop.update(value)

        self._pending_props[name] = prop

    def append(self, *children):
        self._pending_children.extend(children)

    def commit(self):
        """Commit any pending changes to this Page object."""
        num_changes = len(self._pending_props) + len(self._pending_children)

        if num_changes == 0:
            log.debug("no pending changes for page %s; nothing to do", num_changes)
            return

        page_id = self.__data__["id"]  # FIXME why can't we use self.id here??
        log.info("Committing %d changes to page %s...", num_changes, page_id)

        if len(self._pending_props) > 0:
            log.debug(
                "=> committing %d properties :: %s",
                len(self._pending_props),
                self._pending_props,
            )
            self._session.pages.update(page_id, properties=self._pending_props)
            self._pending_props.clear()

        if len(self._pending_children) > 0:
            log.debug(
                "=> committing %d children :: %s",
                len(self._pending_children),
                self._pending_children,
            )
            self._session.blocks.children.append(
                block_id=page_id, children=self._pending_children
            )
            self._pending_children.clear()
