"""Wrapper for Notion API blocks.

Blocks are specifc records that hold content.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .core import NestedObject, TypedObject
from .records import Record
from .types import EmojiObject, FileObject, RichTextObject, TextObject

log = logging.getLogger(__name__)


class Block(Record, TypedObject, object="block"):
    """A standard block object in Notion."""

    # Blocks are Records with a type...


class UnsupportedBlock(Block, type="unsupported"):
    """A placeholder for unsupported blocks in the API."""

    unsupported: Optional[Dict[str, Any]] = None


class TextBlock(Block):
    """A standard text block object in Notion."""

    @classmethod
    def from_text(cls, text):
        text = TextObject.from_value(text)

        if not hasattr(cls, "type") or cls.type is None:
            raise TypeError(f"class type is not defined: {cls}")

        # text types have a nested object with 'type' name and a 'text' child
        # here, we use the local constructor to build out the nested object...

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


class Quote(TextBlock, type="quote"):
    """A quote block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        children: List[Block] = None

    quote: NestedData = None


class Callout(TextBlock, type="callout"):
    """A callout block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = None
        children: List[Block] = None
        icon: Optional[Union[FileObject, EmojiObject]] = None

    callout: NestedData = None


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


class Divider(Block, type="divider"):
    """A divider block in Notion."""

    divider: Any = None


class TableOfContents(Block, type="table_of_contents"):
    """A table_of_contents block in Notion."""

    table_of_contents: Any = None


class Breadcrumb(Block, type="breadcrumb"):
    """A breadcrumb block in Notion."""

    breadcrumb: Any = None


class Embed(Block, type="embed"):
    """An embed block in Notion."""

    class NestedData(NestedObject):
        url: str

    embed: NestedData = None

    @property
    def URL(self):
        return None if self.embed is None else self.embed.url

    @classmethod
    def from_url(cls, url):
        obj = cls.NestedData(url=url)
        return Embed(embed=obj)


class Bookmark(Block, type="bookmark"):
    """A bookmark block in Notion."""

    class NestedData(NestedObject):
        url: str

    bookmark: NestedData = None

    @classmethod
    def from_url(cls, url):
        obj = cls.NestedData(url=url)
        return Bookmark(bookmark=obj)

    @property
    def URL(self):
        return None if self.bookmark is None else self.bookmark.url


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
