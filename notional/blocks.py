"""Wrapper for Notion API blocks.

These objects provide both access to the primitive data structure returned by the API
as well as higher-level access methods.  In general, attributes in lower case represent
the primitive data structure, where capitalized attributes provide higher-level access.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

from .core import NamedObject, NestedObject, TypedObject
from .iterator import EndpointIterator
from .schema import Schema
from .types import EmojiObject, FileObject, PropertyValue, RichTextObject, TextObject

log = logging.getLogger(__name__)


class BlockRef(TypedObject):
    """Reference another block."""

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


class Record(NamedObject):
    """The base type for all Notion API records."""

    id: str = None
    created_time: datetime = None
    last_edited_time: datetime = None
    has_children: bool = False


class Database(Record, object="database"):
    """A database record type."""

    title: List[RichTextObject] = None
    parent: BlockRef = None
    properties: Schema = {}

    @property
    def Title(self):
        return None if self.title is None else "".join(str(text) for text in self.title)


class Page(Record, object="page"):
    """A standard Notion page object."""

    archived: bool = False
    parent: BlockRef = None
    url: str = None
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

    def __setitem__(self, name, prop):
        """Set the object data for the given property.

        :param name: the name of the property to set
        :param prop: the PropertyValue for the named property
        """

        log.debug("set property :: {%s} [%s] => %s", self.id, name, prop)

        self.properties[name] = prop

    @property
    def Title(self):

        if self.properties is None:
            return None

        for prop in self.properties.values():
            if prop.id == "title":
                return prop

        return None


class Block(Record, TypedObject, object="block"):
    """A standard block object in Notion."""


class UnsupportedBlock(Block, type="unsupported"):
    """A placeholder for unsupported blocks in the API."""

    # TODO could/should we store arbitrary fields here?


class TextBlock(Block):
    """A standard text block object in Notion."""

    @classmethod
    def from_text(cls, text):
        text = TextObject.from_value(text)

        if not hasattr(cls, "type") or cls.type is None:
            raise TypeError(f"class type is not defined: {cls}")

        # text types have a nested object with 'type' name and a 'text' child
        # here, we use the constructor to build out the nested object...

        return cls(**{cls.type: {"text": [text]}})


class Paragraph(TextBlock, type="paragraph"):
    """A paragraph block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        children: List[Block] = None

    paragraph: NestedData = None


class Heading1(TextBlock, type="heading_1"):
    """A heading_1 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None

    heading_1: NestedData = None


class Heading2(TextBlock, type="heading_2"):
    """A heading_2 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None

    heading_2: NestedData = None


class Heading3(TextBlock, type="heading_3"):
    """A heading_3 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None

    heading_3: NestedData = None


class BulletedListItem(TextBlock, type="bulleted_list_item"):
    """A bulleted list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        children: List[Block] = None

    bulleted_list_item: NestedData = None


class NumberedListItem(TextBlock, type="numbered_list_item"):
    """A numbered list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        children: List[Block] = None

    numbered_list_item: NestedData = None


class ToDo(TextBlock, type="to_do"):
    """A todo list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        checked: bool = False
        children: List[Block] = None

    to_do: NestedData = None


class Toggle(TextBlock, type="toggle"):
    """A toggle list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        children: List[Block] = None

    toggle: NestedData = None


class Embed(Block, type="embed"):
    """An embed block in Notion."""

    class NestedData(NestedObject):
        url: str

    embed: NestedData = None

    @classmethod
    def from_url(cls, url):
        obj = NestedData(url=url)
        return Embed(embed=obj)


class Bookmark(Block, type="bookmark"):
    """A bookmark block in Notion."""

    class NestedData(NestedObject):
        url: str

    bookmark: NestedData = None

    @classmethod
    def from_url(cls, url):
        obj = NestedData(url=url)
        return Bookmark(bookmark=obj)


class File(Block, type="file"):
    """A file block in Notion."""

    file: FileObject = None


class Image(Block, type="image"):
    """An image block in Notion."""

    image: FileObject = None


class Video(Block, type="video"):
    """A video block in Notion."""

    video: FileObject = None


class PDF(Block, type="pdf"):
    """A pdf block in Notion."""

    pdf: FileObject = None


class ChildPage(Block, type="child_page"):
    """A child page block in Notion."""

    class NestedData(NestedObject):
        title: str

    child_page: NestedData = None
