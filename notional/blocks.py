"""Wrapper for Notion API blocks.

Blocks are specifc records that hold content.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

import logging
from typing import List, Optional, Union

from .core import NestedObject, TypedObject
from .records import Record
from .text import (
    CodingLanguage,
    FullColor,
    RichTextObject,
    TextObject,
    markdown,
    plain_text,
)
from .types import EmojiObject, FileObject

log = logging.getLogger(__name__)


# TODO consider adding helper methods for blocks that support children...


class Block(Record, TypedObject, object="block"):
    """A standard block object in Notion."""

    # Blocks are Records with a type...


class UnsupportedBlock(Block, type="unsupported"):
    """A placeholder for unsupported blocks in the API."""

    class NestedData(NestedObject):
        pass

    unsupported: Optional[NestedData] = None


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


class AppendChildren(object):
    def __iadd__(self, block):
        self.append(block)
        return self

    def append(self, block):
        type = getattr(self, "type", None)

        if type is None:
            raise AttributeError("type not found")

        nested = getattr(self, type)

        if nested is None:
            raise AttributeError("missing nested data")

        if not hasattr(nested, "children"):
            raise AttributeError("nested data does not support children")

        if nested.children is None:
            nested.children = list()

        nested.children.append(block)


class Paragraph(TextBlock, AppendChildren, type="paragraph"):
    """A paragraph block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    paragraph: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.paragraph and self.paragraph.text:
            return markdown(*self.paragraph.text)

        return ""


class Heading1(TextBlock, type="heading_1"):
    """A heading_1 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        color: FullColor = FullColor.default

    heading_1: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.heading_1 and self.heading_1.text:
            return f"# {markdown(*self.heading_1.text)} #"

        return ""


class Heading2(TextBlock, type="heading_2"):
    """A heading_2 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        color: FullColor = FullColor.default

    heading_2: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.heading_2 and self.heading_2.text:
            return f"## {markdown(*self.heading_2.text)} ##"

        return ""


class Heading3(TextBlock, type="heading_3"):
    """A heading_3 block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        color: FullColor = FullColor.default

    heading_3: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.heading_3 and self.heading_3.text:
            return f"### {markdown(*self.heading_3.text)} ###"

        return ""


class Quote(TextBlock, AppendChildren, type="quote"):
    """A quote block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    quote: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.quote and self.quote.text:
            return "> " + markdown(*self.quote.text)

        return ""


class Code(TextBlock, type="code"):
    """A code block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        caption: List[RichTextObject] = []
        language: CodingLanguage = CodingLanguage.plain_text

    code: NestedData = NestedData()

    @property
    def Markdown(self):
        lang = self.code.language if self.code and self.code.language else ""

        # FIXME this is not the standard way to represent code blocks in markdown...

        if self.code and self.code.text:
            return f"```{lang}\n{self.code.text}\n```"

        return ""


class Callout(TextBlock, AppendChildren, type="callout"):
    """A callout block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        icon: Optional[Union[FileObject, EmojiObject]] = None
        color: FullColor = FullColor.default

    callout: NestedData = NestedData()


class BulletedListItem(TextBlock, AppendChildren, type="bulleted_list_item"):
    """A bulleted list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    bulleted_list_item: NestedData = NestedData()

    @property
    def Markdown(self):
        return f"- {super().Markdown}"


class NumberedListItem(TextBlock, AppendChildren, type="numbered_list_item"):
    """A numbered list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    numbered_list_item: NestedData = NestedData()

    @property
    def Markdown(self):
        return f"1. {super().Markdown}"


class ToDo(TextBlock, AppendChildren, type="to_do"):
    """A todo list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        checked: bool = False
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    to_do: NestedData = NestedData()


class Toggle(TextBlock, AppendChildren, type="toggle"):
    """A toggle list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    toggle: NestedData = NestedData()


class Divider(Block, type="divider"):
    """A divider block in Notion."""

    class NestedData(NestedObject):
        pass

    divider: NestedData = NestedData()

    @property
    def Markdown(self):
        return "---"


class TableOfContents(Block, type="table_of_contents"):
    """A table_of_contents block in Notion."""

    class NestedData(NestedObject):
        color: FullColor = FullColor.default

    table_of_contents: NestedData = NestedData()


class Breadcrumb(Block, type="breadcrumb"):
    """A breadcrumb block in Notion."""

    class NestedData(NestedObject):
        pass

    breadcrumb: NestedData = NestedData()


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

    class NestedData(NestedObject):
        pass

    column_list: NestedData = NestedData()


class Column(Block, type="column"):
    """A column block in Notion."""

    class NestedData(NestedObject):
        pass

    column: NestedData = NestedData()


class LinkPreview(Block, type="link_preview"):
    """A link_preview block in Notion."""

    class NestedData(NestedObject):
        url: str = None

    link_preview: NestedData = NestedData()


class Table(Block, type="table"):
    """A table block in Notion."""

    class NestedData(NestedObject):
        table_width: int = 0
        has_column_header: bool = False
        has_row_header: bool = False

    table: NestedData = NestedData()


class TableRow(Block, type="table_row"):
    """A table_row block in Notion."""

    class NestedData(NestedObject):
        cells: List[List[RichTextObject]] = None

    table_row: NestedData = NestedData()


class Template(Block, AppendChildren, type="template"):
    """A template block in Notion."""

    class NestedData(NestedObject):
        rich_text: Optional[List[RichTextObject]] = None
        children: Optional[List[Block]] = None

    template: NestedData = NestedData()
