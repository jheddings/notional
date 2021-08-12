"""Wrapper for Notion API objects."""

import logging
from datetime import datetime
from typing import Dict, List

from .core import DataObject, TypedObject
from .iterator import EndpointIterator
from .schema import Schema
from .types import PropertyValue, RichTextObject

log = logging.getLogger(__name__)


class BlockRef(TypedObject):
    """Reference another block."""

    pass

    # TODO method / property to resolve the reference?


class DatabaseRef(BlockRef, type="database_id"):
    """Reference a database."""

    database_id: str


class PageRef(BlockRef, type="page_id"):
    """Reference a page."""

    page_id: str


class WorkspaceRef(BlockRef, type="workspace"):
    """Reference the workspace."""

    workspace: bool = True


class Block(DataObject):
    """The base type for all Notion blocks."""

    object: str = "block"
    id: str = None
    created_time: datetime = None
    last_edited_time: datetime = None
    has_children: bool = False

    # TODO - update this object from the given data
    # def update(self, **data):


class Database(Block):
    """A database record type."""

    object: str = "database"
    title: List[RichTextObject] = None
    parent: BlockRef = None
    properties: Schema = None

    @property
    def Title(self):
        return None if self.title is None else "".join(str(text) for text in self.title)


class Page(Block):
    """A standard Notion page object."""

    object: str = "page"
    archived: bool = False
    parent: BlockRef = None
    url: str = None
    properties: Dict[str, PropertyValue] = None

    def __getitem__(self, key):
        """Indexer for the given property name."""

        log.debug("get property :: {%s} %s", self.id, key)

        if self.properties is None:
            raise AttributeError("No properties in Page")

        prop = self.properties.get(key)

        if prop is None:
            raise AttributeError(f"No such property: {key}")

        return prop

    def __setitem__(self, key, prop):
        """Set the object data for the given property."""
        self.properties[key] = prop

    def __iadd__(self, child):
        """Append the given child to this Page."""
        self.append(child)

    @property
    def Title(self):
        # TODO would it be better to return an empty object for setting?
        if self.properties is None:
            return None

        for prop in self.properties.values():
            if prop.id == "title":
                return prop

        return None

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""

        return EndpointIterator(
            endpoint=self._session.blocks.children.list, block_id=self.id
        )

    def set_property(self, name, value):
        """Set the raw data for the given property name."""

        log.debug("set property :: {%s} %s => %s", self.id, name, value)

        if self.__data__ is None:
            self.__data__ = dict()

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
        """Append the given blocks as children of this Page."""
        if children is not None and len(children) > 0:
            self._pending_children.extend(children)
            self.has_children = True
