"""Wrapper for Notion API objects."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

from .core import DataObject, TypedObject
from .iterator import EndpointIterator
from .schema import PropertyObject, Schema
from .types import (
    NativePropertyValue,
    PropertyValue,
    RichText,
    RichTextElement,
    notion_to_python,
    python_to_notion,
)

log = logging.getLogger(__name__)


@dataclass
class BlockRef(TypedObject):
    """Reference another block."""

    type: str


@dataclass
class DatabaseRef(BlockRef):
    """Reference a database."""

    __type__ = "database_id"

    database_id: str


@dataclass
class PageRef(BlockRef):
    """Reference a page."""

    __type__ = "page_id"

    page_id: str


@dataclass
class WorkspaceRef(BlockRef):
    """Reference the workspace."""

    __type__ = "workspace"

    workspace: bool = True


@dataclass
class UrlRef(BlockRef):
    """Reference a URL."""

    __type__ = "url"

    url: str = None


@dataclass
class Block(DataObject):
    """The base type for all Notion blocks."""

    object: str = "block"
    id: str = None
    created_time: datetime = None
    last_edited_time: datetime = None
    has_children: bool = False

    # TODO - update this object from the given data
    # def update(self, **data):


@dataclass
class Database(Block):
    """A database record type."""

    object: str = "database"
    title: List[RichText] = None
    parent: BlockRef = None
    properties: Schema = field(default_factory=Schema)

    @classmethod
    def from_json(cls, data):
        if "title" in data and data["title"] is not None:
            data["title"] = [RichTextElement.from_json(text) for text in data["title"]]

        if "properties" in data and data["properties"] is not None:
            data["properties"] = {
                key: PropertyObject.from_json(prop)
                for key, prop in data["properties"].items()
            }

        return super().from_json(data)


@dataclass
class Page(Block):
    """A standard Notion page object."""

    object: str = "page"
    archived: bool = False
    parent: BlockRef = None
    url: str = None
    properties: Dict[str, PropertyValue] = field(default_factory=dict)

    def __post_init__(self):
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
    def Title(self):
        # TODO would it be better to return an empty object for setting?
        if self.properties is None:
            return None

        for prop in self.properties:
            if prop.id == "title":
                return prop

        return None

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
        """Append the given blocks as children of this Page."""
        if children is not None and len(children) > 0:
            self._pending_children.extend(children)
            self.has_children = True

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
