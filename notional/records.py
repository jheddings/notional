"""Wrapper for Notion API data types.

We handle databases and pages somewhat differently than other blocks since they
represent top-level containers for other blocks.

These objects provide both access to the primitive data structure returned by the API
as well as higher-level access methods.  In general, attributes in lower case represent
the primitive data structure, where capitalized attributes provide higher-level access.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from .core import NamedObject, TypedObject
from .schema import PropertyObject
from .text import plain_text
from .types import EmojiObject, FileObject, PropertyValue, RichTextObject

log = logging.getLogger(__name__)


class ParentRef(TypedObject):
    """Reference another block."""

    # TODO method / property to resolve the reference?


class DatabaseParent(ParentRef, type="database_id"):
    """Reference a database."""

    database_id: UUID


class PageParent(ParentRef, type="page_id"):
    """Reference a page."""

    page_id: UUID


class WorkspaceParent(ParentRef, type="workspace"):
    """Reference the workspace."""

    workspace: bool = True


class Record(NamedObject):
    """The base type for Notion API records."""

    id: UUID = None
    created_time: datetime = None
    last_edited_time: datetime = None
    has_children: bool = False
    archived: bool = False


class Database(Record, object="database"):
    """A database record type."""

    title: List[RichTextObject] = None
    url: str = None
    parent: ParentRef = None
    icon: Optional[Union[FileObject, EmojiObject]] = None
    cover: Optional[FileObject] = None
    properties: Dict[str, PropertyObject] = {}

    @property
    def Title(self):
        if self.title is None:
            return None

        return plain_text(*self.title)


class Page(Record, object="page"):
    """A standard Notion page object."""

    url: str = None
    parent: ParentRef = None
    icon: Optional[Union[FileObject, EmojiObject]] = None
    cover: Optional[FileObject] = None
    properties: Dict[str, PropertyValue] = {}

    def __getitem__(self, name):
        """Indexer for the given property name.

        :param name: the name of the property to get
        """

        log.debug("get property :: {%s} [%s]", self.id, name)

        if self.properties is None:
            raise AttributeError("No properties in Page")

        prop = self.properties.get(name)

        if prop is None:
            raise AttributeError(f"No such property: {name}")

        return prop

    def __setitem__(self, name, value):
        """Set the object data for the given property.

        :param name: the name of the property to set
        :param prop: the PropertyValue for the named property
        """

        log.debug("set property :: {%s} [%s] => %s", self.id, name, value)

        if not isinstance(value, PropertyValue):
            raise ValueError(f"Unable to set {name} :: unsupported value type")

        self.properties[name] = value

    @property
    def Title(self):
        if self.properties is None:
            return None

        for prop in self.properties.values():
            if prop.id == "title":
                return prop.Value

        return None
