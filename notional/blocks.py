"""Wrapper for Notion API blocks.

Blocks are specifc records that hold content.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

import logging
from typing import List, Optional, Union

from .core import NestedObject, TypedObject
from .records import BlockRef, ParentRef, Record
from .text import (
    CodingLanguage,
    FullColor,
    RichTextObject,
    TextObject,
    chunky,
    markdown,
    plain_text,
)
from .types import EmojiObject, FileObject

log = logging.getLogger(__name__)


class Block(Record, TypedObject, object="block"):
    """A standard block object in Notion.

    Calling the block will expose the nested data in the object.
    """


class UnsupportedBlock(Block, type="unsupported"):
    """A placeholder for unsupported blocks in the API."""

    class NestedData(NestedObject):
        pass

    unsupported: Optional[NestedData] = None


class TextBlock(Block):
    """A standard text block object in Notion."""

    # text blocks have a nested object with 'type' name and a 'text' child

    @property
    def __text__(self):
        """Provide short-hand access to the nested text content in this block."""

        return self("text")

    def concat(self, *text):
        """Concatenate text (either `RichTextObject` or `str` items) to this block."""

        if text is None:
            raise AttributeError("text cannot be None")

        nested = self()

        if not hasattr(nested, "text"):
            raise AttributeError("nested data does not contain text")

        if nested.text is None:
            nested.text = []

        for obj in text:
            if obj is None:
                continue

            if isinstance(obj, RichTextObject):
                nested.text.append(obj)

            elif isinstance(obj, str):
                for chunk in chunky(obj):
                    nested.text.append(TextObject.from_value(chunk))

            else:
                raise ValueError("unsupported text object")

    @classmethod
    def from_text(cls, *text):
        if text is None:
            return None

        obj = cls()
        obj.concat(*text)

        return obj

    @property
    def PlainText(self):
        """Return the contents of this Block as plain text."""

        content = self.__text__

        return None if content is None else plain_text(*content)


class WithChildrenMixin:
    """Mixin for blocks that support children blocks."""

    @property
    def __children__(self):
        """Provide short-hand access to the children in this block."""

        return self("children")

    def __iadd__(self, block):
        self.append(block)
        return self

    def append(self, block):
        """Append the given block to the children of this block."""

        if block is None:
            raise AttributeError("block cannot be None")

        nested = self()

        if nested.children is None:
            nested.children = []

        nested.children.append(block)

        self.has_children = True


class Paragraph(TextBlock, WithChildrenMixin, type="paragraph"):
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


class Quote(TextBlock, WithChildrenMixin, type="quote"):
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
            return f"```{lang}\n{markdown(*self.code.text)}\n```"

        return ""


class Callout(TextBlock, WithChildrenMixin, type="callout"):
    """A callout block in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        icon: Optional[Union[FileObject, EmojiObject]] = None
        color: FullColor = FullColor.default

    callout: NestedData = NestedData()


class BulletedListItem(TextBlock, WithChildrenMixin, type="bulleted_list_item"):
    """A bulleted list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    bulleted_list_item: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.bulleted_list_item and self.bulleted_list_item.text:
            return f"- {markdown(*self.bulleted_list_item.text)}"

        return ""


class NumberedListItem(TextBlock, WithChildrenMixin, type="numbered_list_item"):
    """A numbered list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    numbered_list_item: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.numbered_list_item and self.numbered_list_item.text:
            return f"1. {markdown(*self.numbered_list_item.text)}"

        return ""


class ToDo(TextBlock, WithChildrenMixin, type="to_do"):
    """A todo list item in Notion."""

    class NestedData(NestedObject):
        text: List[RichTextObject] = []
        checked: bool = False
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.default

    to_do: NestedData = NestedData()

    @property
    def Markdown(self):
        if self.to_do and self.to_do.text:
            if self.to_do.checked:
                return f"- [x] {markdown(*self.to_do.text)}"

            return f"- [ ] {markdown(*self.to_do.text)}"

        return ""


class Toggle(TextBlock, WithChildrenMixin, type="toggle"):
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
        return self.embed.url

    @property
    def Markdown(self):
        if self.embed and self.emdeb.url:
            return f"<{self.embed.url}>"

        return ""

    @classmethod
    def from_url(cls, url):
        nested = cls.NestedData(url=url)
        return Embed(embed=nested)


class Bookmark(Block, type="bookmark"):
    """A bookmark block in Notion."""

    class NestedData(NestedObject):
        url: str = None
        caption: Optional[List[RichTextObject]] = None

    bookmark: NestedData = NestedData()

    @property
    def URL(self):
        return self.bookmark.url

    @property
    def Markdown(self):
        if self.bookmark and self.bookmark.url:
            return f"<{self.bookmark.url}>"

        return ""

    @classmethod
    def from_url(cls, url):
        nested = cls.NestedData(url=url)
        return Bookmark(bookmark=nested)


class LinkPreview(Block, type="link_preview"):
    """A link_preview block in Notion."""

    class NestedData(NestedObject):
        url: str = None

    link_preview: NestedData = NestedData()

    @property
    def URL(self):
        return self.link_preview.url

    @property
    def Markdown(self):
        if self.link_preview and self.link_preview.url:
            return f"<{self.link_preview.url}>"

        return ""

    @classmethod
    def from_url(cls, url):
        nested = cls.NestedData(url=url)
        return LinkPreview(link_preview=nested)


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


class TableRow(Block, type="table_row"):
    """A table_row block in Notion."""

    class NestedData(NestedObject):
        cells: List[List[RichTextObject]] = None

    table_row: NestedData = NestedData()

    def append(self, text):
        if self.table_row.cells is None:
            self.table_row.cells = []

        if isinstance(text, list):
            self.table_row.cells.append(list)

        elif isinstance(text, RichTextObject):
            self.table_row.cells.append([text])

        else:
            rtf = TextObject.from_value(text)
            self.table_row.cells.append([rtf])

    @property
    def Width(self):
        return len(self.table_row.cells) if self.table_row.cells else 0


class Table(Block, WithChildrenMixin, type="table"):
    """A table block in Notion."""

    class NestedData(NestedObject):
        table_width: int = 0
        has_column_header: bool = False
        has_row_header: bool = False

        # note that children will not be populated when getting this block
        # https://developers.notion.com/reference/block#table-blocks
        children: Optional[List[TableRow]] = []

    table: NestedData = NestedData()

    def append(self, block: TableRow):
        # when creating a new table via the API, we must provide at least one row
        # XXX need to review whether this is applicable during update...  may need
        # to raise an error if the block has already been created on the server

        if not isinstance(block, TableRow):
            raise ValueError("Only TableRow may be appended to Table blocks.")

        if self.Width == 0:
            self.table.table_width = block.Width
        elif self.Width != block.Width:
            raise ValueError("Number of cells in row must match table")

        self.table.children.append(block)

    @property
    def Width(self):
        return self.table.table_width


class LinkToPage(Block, type="link_to_page"):
    """A link_to_page block in Notion."""

    link_to_page: ParentRef


class SyncedBlock(Block, WithChildrenMixin, type="synced_block"):
    """A synced_block block in Notion - either original or synced."""

    class NestedData(NestedObject):
        synced_from: Optional[BlockRef] = None
        children: Optional[List[Block]] = None

    synced_block: NestedData = NestedData()

    @property
    def IsOriginal(self):
        return self.synced_block.synced_from is None


class Template(Block, WithChildrenMixin, type="template"):
    """A template block in Notion."""

    class NestedData(NestedObject):
        rich_text: Optional[List[RichTextObject]] = None
        children: Optional[List[Block]] = None

    template: NestedData = NestedData()
