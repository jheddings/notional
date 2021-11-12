"""Wrapper for Notion API blocks.

Blocks are specifc records that hold content.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .core import NestedObject, TypedObject
from .records import Record
from .text import CodingLanguage, RichTextObject, TextObject, plain_text
from .types import EmojiObject, FileObject

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

        # TODO split long text blocks into multiple (rather than truncate)?
        obj = TextObject.from_value(text[:2000])

        if not hasattr(cls, "type") or cls.type is None:
            raise TypeError(f"class type is not defined: {cls}")

        # text types have a nested object with 'type' name and a 'text' child
        # here, we use the local constructor to build out the nested object...

        # TODO convert markdown to RichText elements

        log.debug("%s => from_text :: %s", cls.type, text[:10])

        return cls(**{cls.type: {"text": [obj]}})

    @property
    def PlainText(self):
        # content is stored in the nested data, named by the object type
        content = getattr(self, self.__class__.type)
        return plain_text(*content.text)


class Paragraph(TextBlock, type="paragraph"):
    """A paragraph block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None

    paragraph: NestedData = NestedData()


class Heading1(TextBlock, type="heading_1"):
    """A heading_1 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []

    heading_1: NestedData = NestedData()


class Heading2(TextBlock, type="heading_2"):
    """A heading_2 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []

    heading_2: NestedData = NestedData


class Heading3(TextBlock, type="heading_3"):
    """A heading_3 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []

    heading_3: NestedData = NestedData()


class Quote(TextBlock, type="quote"):
    """A quote block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None

    quote: NestedData = NestedData()


class Code(TextBlock, type="code"):
    """A code block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        language: CodingLanguage = CodingLanguage.plain_text

    code: NestedData = NestedData()


class Callout(TextBlock, type="callout"):
    """A callout block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        icon: Optional[Union[FileObject, EmojiObject]] = None

    callout: NestedData = NestedData()


class BulletedListItem(TextBlock, type="bulleted_list_item"):
    """A bulleted list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None

    bulleted_list_item: NestedData = NestedData()


class NumberedListItem(TextBlock, type="numbered_list_item"):
    """A numbered list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None

    numbered_list_item: NestedData = NestedData()


class ToDo(TextBlock, type="to_do"):
    """A todo list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        checked: bool = False
        children: Optional[List[Block]] = None

    to_do: NestedData = NestedData()


class Toggle(TextBlock, type="toggle"):
    """A toggle list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None

    toggle: NestedData = NestedData()


class Divider(Block, type="divider"):
    """A divider block in Notion."""

    divider: Any = dict()


class TableOfContents(Block, type="table_of_contents"):
    """A table_of_contents block in Notion."""

    table_of_contents: Any = dict()


class Breadcrumb(Block, type="breadcrumb"):
    """A breadcrumb block in Notion."""

    breadcrumb: Any = dict()


class Embed(Block, type="embed"):
    """An embed block in Notion."""

    class NestedData(NestedObject):
        url: str = None

    embed: NestedData = NestedData()

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
        url: str = None
        caption: Optional[List[RichTextObject]] = None

    bookmark: NestedData = NestedData()

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
        title: str = None

    child_page: NestedData = NestedData()


class ChildDatabase(Block, type="child_database"):
    """A child database block in Notion."""

    class NestedData(NestedObject):
        title: str = None

    child_database: NestedData = NestedData()


class ColumnList(Block, type="column_list"):
    """A column list block in Notion."""

    column_list: Any = dict()

    # TODO convenience method to get child columns


class Column(Block, type="column"):
    """A column block in Notion."""

    column: Any = dict()

    # TODO convenience method to get child blocks


class LinkPreview(Block, type="link_preview"):
    """A link_preview block in Notion."""

    class NestedData(NestedObject):
        url: str = None

    link_preview: NestedData = NestedData()
