"""Wrapper for Notion API blocks.

Blocks are the base for all Notion content.
"""

from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import Field

from .core import DataObject, NotionObject, TypedObject
from .schema import PropertyObject
from .text import (
    CodingLanguage,
    FullColor,
    RichTextObject,
    TextObject,
    markdown,
    plain_text,
    rich_text,
)
from .types import (
    BlockRef,
    EmojiObject,
    ExternalFile,
    FileObject,
    ParentRef,
    PropertyValue,
)
from .user import PartialUser


class DataRecord(DataObject, ABC):
    """The base type for all Notion API records."""

    parent: Optional[ParentRef] = None
    has_children: bool = False

    archived: bool = False

    created_time: Optional[datetime] = None
    created_by: Optional[PartialUser] = None

    last_edited_time: Optional[datetime] = None
    last_edited_by: Optional[PartialUser] = None


class Database(DataRecord):
    """A database record type."""

    object: Literal["database"] = "database"
    title: List[RichTextObject] = []
    url: Optional[str] = None
    icon: Optional[FileObject] = None
    cover: Optional[ExternalFile] = None
    properties: Dict[str, PropertyObject] = {}
    description: Optional[List[RichTextObject]] = None
    is_inline: bool = False

    @property
    def Title(self):
        """Return the title of this database as plain text."""
        if self.title is None or len(self.title) == 0:
            return None

        return plain_text(*self.title)


class Page(DataRecord):
    """A standard Notion page object."""

    object: Literal["page"] = "page"
    url: Optional[str] = None
    icon: Optional[FileObject] = None
    cover: Optional[ExternalFile] = None
    properties: Dict[str, PropertyValue] = {}

    def __getitem__(self, name):
        """Indexer for the given property name.

        :param name: the name of the property to get from the internal properties
        """

        prop = self.properties.get(name)

        if prop is None:
            raise AttributeError(f"No such property: {name}")

        return prop

    def __setitem__(self, name, value):
        """Set the object data for the given property.

        If `value` is `None`, the property data will be deleted from the page.  This
        does not affect the schema of the page, only the contents of the property.

        :param name: the name of the property to set in the internal properties
        :param value: the new value for the given property
        """

        if value is None:
            self.properties.pop(name, None)

        elif isinstance(value, PropertyValue):
            self.properties[name] = value

        else:
            raise ValueError(f"Unable to set {name} :: unsupported value type")

    @property
    def Title(self):
        """Return the title of this page as a string.

        The title of a page is stored in its properties.  This method will examine the
        page properties, looking for the appropriate `title` entry and return as a
        string.
        """

        # the 'title' property may (or may not) be indexed by name...  especially in
        # the case of # database pages.  the only reliable way to find the title is by
        # scanning each property.

        for prop in self.properties.values():
            if prop.id == "title":
                return prop.Value

        return None


class Block(DataRecord, TypedObject, ABC):
    """A standard block object in Notion.

    Calling the block will expose the nested data in the object.
    """

    object: Literal["block"] = "block"


class UnsupportedBlock(Block):
    """A placeholder for unsupported blocks in the API."""

    unsupported: Optional[Any] = {}
    type: Literal["unsupported"] = "unsupported"


class TextBlock(Block, ABC):
    """A standard text block object in Notion."""

    # text blocks have a nested object with 'type' name and a 'rich_text' child

    @property
    def __text__(self) -> List[RichTextObject]:
        """Provide shorthand access to the nested text content in this block."""

        # calling the block returns the nested data...  this helps deal with
        # subclasses of `TextBlock` that each have different "type" attributes

        return self("rich_text")

    @classmethod
    def __compose__(cls, *text):
        """Compose a `TextBlock` from the given text items."""

        obj = cls()
        obj.concat(*text)

        return obj

    def concat(self, *text):
        """Concatenate text (either `RichTextObject` or `str` items) to this block."""
        rtf = rich_text(*text)
        self.__text__.extend(rtf)

    @property
    def PlainText(self):
        """Return the contents of this Block as plain text."""

        # retrieve the nested text content and convert to plain text
        content = self.__text__

        if content is None:
            return None

        return plain_text(*content)


class WithChildrenMixin:
    """Mixin for blocks that support children blocks."""

    @property
    def __children__(self):
        """Provide short-hand access to the children in this block."""

        return self("children")

    def __iadd__(self, block):
        """Append the given block to the children of this parent in place."""
        self.append(block)
        return self

    def append(self, block):
        """Append the given block to the children of this parent."""

        if block is None:
            raise ValueError("block cannot be None")

        nested = self()

        if nested.children is None:
            nested.children = []

        nested.children.append(block)

        self.has_children = True


class Paragraph(TextBlock, WithChildrenMixin):
    """A paragraph block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.DEFAULT

    paragraph: _NestedData = Field(default_factory=_NestedData)
    type: Literal["paragraph"] = "paragraph"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.paragraph and self.paragraph.rich_text:
            return markdown(*self.paragraph.rich_text)

        return ""


class Heading1(TextBlock):
    """A heading_1 block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        color: FullColor = FullColor.DEFAULT

    heading_1: _NestedData = Field(default_factory=_NestedData)
    type: Literal["heading_1"] = "heading_1"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.heading_1 and self.heading_1.rich_text:
            return f"# {markdown(*self.heading_1.rich_text)} #"

        return ""


class Heading2(TextBlock):
    """A heading_2 block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        color: FullColor = FullColor.DEFAULT

    heading_2: _NestedData = Field(default_factory=_NestedData)
    type: Literal["heading_2"] = "heading_2"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.heading_2 and self.heading_2.rich_text:
            return f"## {markdown(*self.heading_2.rich_text)} ##"

        return ""


class Heading3(TextBlock):
    """A heading_3 block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        color: FullColor = FullColor.DEFAULT

    heading_3: _NestedData = Field(default_factory=_NestedData)
    type: Literal["heading_3"] = "heading_3"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.heading_3 and self.heading_3.rich_text:
            return f"### {markdown(*self.heading_3.rich_text)} ###"

        return ""


class Quote(TextBlock, WithChildrenMixin):
    """A quote block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.DEFAULT

    quote: _NestedData = Field(default_factory=_NestedData)
    type: Literal["quote"] = "quote"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.quote and self.quote.rich_text:
            return "> " + markdown(*self.quote.rich_text)

        return ""


class Code(TextBlock):
    """A code block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        caption: List[RichTextObject] = []
        language: CodingLanguage = CodingLanguage.PLAIN_TEXT

    code: _NestedData = Field(default_factory=_NestedData)
    type: Literal["code"] = "code"

    @classmethod
    def __compose__(cls, text, lang=CodingLanguage.PLAIN_TEXT):
        """Compose a `Code` block from the given text and language."""
        block = super().__compose__(text)
        block.code.language = lang
        return block

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        lang = self.code.language.value if self.code and self.code.language else ""

        # FIXME this is not the standard way to represent code blocks in markdown...

        if self.code and self.code.rich_text:
            return f"```{lang}\n{markdown(*self.code.rich_text)}\n```"

        return ""


class Callout(TextBlock, WithChildrenMixin):
    """A callout block in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        icon: Optional[Union[FileObject, EmojiObject]] = None
        color: FullColor = FullColor.GRAY_BACKGROUND

    callout: _NestedData = Field(default_factory=_NestedData)
    type: Literal["callout"] = "callout"

    @classmethod
    def __compose__(cls, text, emoji=None, color=FullColor.GRAY_BACKGROUND):
        """Compose a `Callout` block from the given text, emoji and color."""

        if emoji is not None:
            emoji = EmojiObject[emoji]

        nested = Callout._NestedData(icon=emoji, color=color)

        callout = cls(callout=nested)
        callout.concat(text)

        return callout


class BulletedListItem(TextBlock, WithChildrenMixin):
    """A bulleted list item in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.DEFAULT

    bulleted_list_item: _NestedData = Field(default_factory=_NestedData)
    type: Literal["bulleted_list_item"] = "bulleted_list_item"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.bulleted_list_item and self.bulleted_list_item.rich_text:
            return f"- {markdown(*self.bulleted_list_item.rich_text)}"

        return ""


class NumberedListItem(TextBlock, WithChildrenMixin):
    """A numbered list item in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.DEFAULT

    numbered_list_item: _NestedData = Field(default_factory=_NestedData)
    type: Literal["numbered_list_item"] = "numbered_list_item"

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.numbered_list_item and self.numbered_list_item.rich_text:
            return f"1. {markdown(*self.numbered_list_item.rich_text)}"

        return ""


class ToDo(TextBlock, WithChildrenMixin):
    """A todo list item in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        checked: bool = False
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.DEFAULT

    to_do: _NestedData = Field(default_factory=_NestedData)
    type: Literal["to_do"] = "to_do"

    @classmethod
    def __compose__(cls, text, checked=False, href=None):
        """Compose a ToDo block from the given text and checked state."""
        txt = TextObject[text, href]

        nested = ToDo._NestedData(
            checked=checked,
            rich_text=[txt],
        )

        return cls(to_do=nested)

    @property
    def IsChecked(self):
        """Determine if this ToDo is marked as checked or not.

        If the block is empty (e.g. no nested data), this method returns `None`.
        """
        return self.to_do.checked if self.to_do else None

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.to_do and self.to_do.rich_text:
            if self.to_do.checked:
                return f"- [x] {markdown(*self.to_do.rich_text)}"

            return f"- [ ] {markdown(*self.to_do.rich_text)}"

        return ""


class Toggle(TextBlock, WithChildrenMixin):
    """A toggle list item in Notion."""

    class _NestedData(NotionObject):
        rich_text: List[RichTextObject] = []
        children: Optional[List[Block]] = None
        color: FullColor = FullColor.DEFAULT

    toggle: _NestedData = Field(default_factory=_NestedData)
    type: Literal["toggle"] = "toggle"


class Divider(Block):
    """A divider block in Notion."""

    type: Literal["divider"] = "divider"
    divider: Optional[Any] = {}

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""
        return "---"


class TableOfContents(Block):
    """A table_of_contents block in Notion."""

    class _NestedData(NotionObject):
        color: FullColor = FullColor.DEFAULT

    table_of_contents: _NestedData
    type: Literal["table_of_contents"] = "table_of_contents"


class Breadcrumb(Block):
    """A breadcrumb block in Notion."""

    breadcrumb: Optional[Any] = {}
    type: Literal["breadcrumb"] = "breadcrumb"


class Embed(Block):
    """An embed block in Notion."""

    class _NestedData(NotionObject):
        url: str

    embed: _NestedData
    type: Literal["embed"] = "embed"

    @classmethod
    def __compose__(cls, url):
        """Create a new `Embed` block from the given URL."""
        nested = Embed._NestedData(url=url)
        return cls(embed=nested)

    @property
    def URL(self):
        """Return the URL contained in this `Embed` block."""
        return self.embed.url

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.embed and self.embed.url:
            return f"<{self.embed.url}>"

        return ""


class Bookmark(Block):
    """A bookmark block in Notion."""

    class _NestedData(NotionObject):
        url: str
        caption: Optional[List[RichTextObject]] = None

    bookmark: _NestedData
    type: Literal["bookmark"] = "bookmark"

    @classmethod
    def __compose__(cls, url):
        """Compose a new `Bookmark` block from a specific URL."""
        nested = Bookmark._NestedData(url=url)
        return cls(bookmark=nested)

    @property
    def URL(self):
        """Return the URL contained in this `Bookmark` block."""
        return self.bookmark.url

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.bookmark and self.bookmark.url:
            return f"<{self.bookmark.url}>"

        return ""


class LinkPreview(Block):
    """A link_preview block in Notion."""

    class _NestedData(NotionObject):
        url: str

    link_preview: _NestedData
    type: Literal["link_preview"] = "link_preview"

    @classmethod
    def __compose__(cls, url):
        """Create a new `LinkPreview` block from the given URL."""
        nested = LinkPreview._NestedData(url=url)
        return cls(link_preview=nested)

    @property
    def URL(self):
        """Return the URL contained in this `LinkPreview` block."""
        return self.link_preview.url

    @property
    def Markdown(self):
        """Return the contents of this block as markdown text."""

        if self.link_preview and self.link_preview.url:
            return f"<{self.link_preview.url}>"

        return ""


class Equation(Block):
    """An equation block in Notion."""

    class _NestedData(NotionObject):
        expression: str

    equation: _NestedData
    type: Literal["equation"] = "equation"

    @classmethod
    def __compose__(cls, expr):
        """Create a new `Equation` block from the given expression."""
        nested = Equation._NestedData(expression=expr)
        return cls(equation=nested)


class File(Block):
    """A file block in Notion."""

    file: FileObject
    type: Literal["file"] = "file"


class Image(Block):
    """An image block in Notion."""

    image: FileObject
    type: Literal["image"] = "image"


class Video(Block):
    """A video block in Notion."""

    video: FileObject
    type: Literal["video"] = "video"


class PDF(Block):
    """A pdf block in Notion."""

    pdf: FileObject
    type: Literal["pdf"] = "pdf"


class ChildPage(Block):
    """A child page block in Notion."""

    class _NestedData(NotionObject):
        title: str

    child_page: _NestedData
    type: Literal["child_page"] = "child_page"


class ChildDatabase(Block):
    """A child database block in Notion."""

    class _NestedData(NotionObject):
        title: str

    child_database: _NestedData
    tpye: Literal["child_database"] = "child_database"


class Column(Block, WithChildrenMixin):
    """A column block in Notion."""

    class _NestedData(NotionObject):
        # note that children will not be populated when getting this block
        # https://developers.notion.com/changelog/column-list-and-column-support
        children: Optional[List[Block]] = None

    column: _NestedData
    type: Literal["column"] = "column"

    @classmethod
    def __compose__(cls, *blocks):
        """Create a new `Column` block with the given blocks as children."""
        col = cls()

        for block in blocks:
            col.append(block)

        return col


class ColumnList(Block, WithChildrenMixin):
    """A column list block in Notion."""

    class _NestedData(NotionObject):
        # note that children will not be populated when getting this block
        # https://developers.notion.com/changelog/column-list-and-column-support
        children: Optional[List[Column]] = None

    column_list: _NestedData
    type: Literal["column_list"] = "column_list"

    @classmethod
    def __compose__(cls, *columns):
        """Create a new `Column` block with the given blocks as children."""
        cols = cls()

        for col in columns:
            cols.append(col)

        return cols


class TableRow(Block):
    """A table_row block in Notion."""

    class _NestedData(NotionObject):
        cells: List[List[RichTextObject]] = []

        def __getitem__(self, col):
            """Return the cell content for the requested column.

            This will raise an `IndexError` if there are not enough columns.
            """
            if col > len(self.cells):
                raise IndexError()

            return self.cells[col]

    table_row: _NestedData = Field(default_factory=_NestedData)
    type: Literal["table_row"] = "table_row"

    def __getitem__(self, cell_num):
        """Return the cell content for the requested column."""
        return self.table_row[cell_num]

    @classmethod
    def __compose__(cls, *cells):
        """Create a new `TableRow` block with the given cell contents."""
        row = cls()

        for cell in cells:
            row.append(cell)

        return row

    def append(self, text):
        """Append the given text as a new cell in this `TableRow`.

        `text` may be a string, `RichTextObject` or a list of `RichTextObject`'s.

        :param text: the text content to append
        """
        if self.table_row.cells is None:
            self.table_row.cells = []

        if isinstance(text, list):
            self.table_row.cells.append(list)

        elif isinstance(text, RichTextObject):
            self.table_row.cells.append([text])

        else:
            rtf = TextObject[text]
            self.table_row.cells.append([rtf])

    @property
    def Width(self):
        """Return the width (number of cells) in this `TableRow`."""
        return len(self.table_row.cells) if self.table_row.cells else 0


class Table(Block, WithChildrenMixin):
    """A table block in Notion."""

    class _NestedData(NotionObject):
        table_width: int = 0
        has_column_header: bool = False
        has_row_header: bool = False

        # note that children will not be populated when getting this block
        # https://developers.notion.com/reference/block#table-blocks
        children: Optional[List[TableRow]] = []

    table: _NestedData = Field(default_factory=_NestedData)
    type: Literal["table"] = "table"

    @classmethod
    def __compose__(cls, *rows):
        """Create a new `Table` block with the given rows."""
        table = cls()

        for row in rows:
            table.append(row)

        return table

    def append(self, block: TableRow):
        """Append the given row to this table.

        This method is only applicable when creating a new `Table` block.  In order to
        add rows to an existing `Table`, use the `blocks.children.append()` endpoint.

        When adding a row, this method will rase an exception if the width does not
        match the expected number of cells for existing rows in the block.
        """

        # XXX need to review whether this is applicable during update...  may need
        # to raise an error if the block has already been created on the server

        if not isinstance(block, TableRow):
            raise ValueError("Only TableRow may be appended to Table blocks.")

        if self.Width == 0:
            self.table.table_width = block.Width
        elif self.Width != block.Width:
            raise ValueError("Number of cells in row must match table")

        if self.table.children is None:
            self.table.children = [block]
        else:
            self.table.children.append(block)

    @property
    def Width(self):
        """Return the current width of this table."""
        return self.table.table_width


class LinkToPage(Block):
    """A link_to_page block in Notion."""

    link_to_page: ParentRef
    type: Literal["link_to_page"] = "link_to_page"


class SyncedBlock(Block, WithChildrenMixin):
    """A synced_block block in Notion - either original or synced."""

    class _NestedData(NotionObject):
        synced_from: Optional[BlockRef] = None
        children: Optional[List[Block]] = None

    synced_block: _NestedData
    type: Literal["synced_block"] = "synced_block"

    @property
    def IsOriginal(self):
        """Determine if this block represents the original content.

        If this method returns `False`, the block represents the sync'ed block.
        """
        return self.synced_block.synced_from is None


class Template(Block, WithChildrenMixin):
    """A template block in Notion."""

    class _NestedData(NotionObject):
        rich_text: Optional[List[RichTextObject]] = None
        children: Optional[List[Block]] = None

    template: _NestedData
    type: Literal["template"] = "template"
