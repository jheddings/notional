"""Elements for working with rich text in Notion."""

from dataclasses import dataclass
from typing import Dict, List

from .core import DataObject, NestedObject


@dataclass
class Annotations(object):
    """Style information for RichTextElement's."""

    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = None

    @property
    def is_plain(self):
        if self.bold:
            return False
        if self.italic:
            return False
        if self.strikethrough:
            return False
        if self.underline:
            return False
        if self.code:
            return False
        if self.color is not None:
            return False
        return True


@dataclass
class RichTextElement(DataObject):
    """Base class for Notion rich text elements."""

    type: str
    plain_text: str = None
    href: str = None
    annotations: Annotations = None

    def __str__(self):
        """Return a string representation of this object."""
        return self.plain_text

    @classmethod
    def from_json(cls, data):
        """Override the default method to provide a factory for subclass types."""

        # prevent infinite loops from subclasses...
        if cls == RichTextElement:
            data_type = data.get("type")

            if data_type == "text":
                return TextElement.from_json(data)

        return super().from_json(data)


@dataclass
class TextElement(RichTextElement):
    """Notion text element."""

    @dataclass
    class NestedText(NestedObject):
        content: str = None
        link: str = None

    text: NestedText = None
