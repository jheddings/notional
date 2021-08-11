"""Wrapper for Notion API data types."""

from datetime import date, datetime
from typing import Dict, List, Optional, Union

from .core import DataObject, NestedObject, TypedObject
from .schema import SelectOption
from .user import User


class Annotations(DataObject):
    """Style information for RichTextObject's."""

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


class LinkObject(DataObject):
    """Reference a URL."""

    type: str = "url"
    url: str = None


class RichTextObject(TypedObject):
    """Base class for Notion rich text elements."""

    plain_text: str
    href: str = None
    annotations: Annotations = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.href is None:
            return self.plain_text

        return f"[{self.plain_text}]({self.href})"


class TextObject(RichTextObject):
    """Notion text element."""

    __type__ = "text"

    class NestedText(NestedObject):
        content: str
        link: LinkObject = None

    text: NestedText = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.text is None:
            return None

        return self.text.content


class PageRef(DataObject):
    id: str


class MentionObject(RichTextObject):
    """Notion mention element."""

    __type__ = "mention"

    class NestedMention(NestedObject, TypedObject):
        pass

    class MentionUser(NestedMention):
        user: User

    class MentionPage(NestedMention):
        page: PageRef

    class MentionDatabase(NestedMention):
        database: PageRef

    mention: NestedMention = None


class EquationObject(RichTextObject):
    """Notion equation element."""

    __type__ = "equation"

    class NestedEquation(NestedObject):
        expression: str

    equation: NestedEquation = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.equation is None:
            return None

        return self.equation.expression

    @classmethod
    def from_value(cls, value):
        """Create a new Equation mention from the given LaTeX string."""
        inner = NestedEquation(expression=value)
        return cls(equation=inner)


class PropertyValue(TypedObject):
    """Base class for Notion property values."""

    id: str = None

    @classmethod
    def from_value(cls, value):
        """Create a new instance of this property from the given value."""
        raise NotImplementedError()


class Title(PropertyValue):
    """Notion title type."""

    __type__ = "title"

    title: List[RichTextObject] = []

    def __str__(self):
        """Return a string representation of this object."""

        if self.title is None:
            return None

        return "".join(str(text) for text in self.title)


class RichText(PropertyValue):
    """Notion rich text type."""

    __type__ = "rich_text"

    rich_text: List[RichTextObject] = []

    def __str__(self):
        """Return a string representation of this object."""

        if self.rich_text is None:
            return None

        return "".join(str(rich_text) for text in self.rich_text)


class Number(PropertyValue):
    """Simple number type."""

    __type__ = "number"

    number: Union[int, float] = None

    def __str__(self):
        """Return a string representation of this object."""
        return str(self.number)

    def __eq__(self, other):
        """Determine if this property is equal to the given object."""
        return self.number == other

    def __ne__(self, other):
        """Determine if this property is not equal to the given object."""
        return self.number != other

    def __iadd__(self, other):
        """Add the given value to this Number."""
        self.number += other

    def __isub__(self, other):
        """Subtract the given value from this Number."""
        self.number -= other

    @classmethod
    def from_value(cls, value):
        """Create a new Number from the native value."""
        return cls(number=value)


class Checkbox(PropertyValue):
    """Simple checkbox type; represented as a boolean."""

    __type__ = "checkbox"

    checkbox: bool = None

    def __str__(self):
        """Return a string representation of this object."""
        return str(self.checkbox)

    def __eq__(self, other):
        """Determine if this property is equal to the given object."""
        return self.checkbox == other

    def __ne__(self, other):
        """Determine if this property is not equal to the given object."""
        return self.checkbox != other

    @classmethod
    def from_value(cls, value):
        """Create a new Checkbox from the native value."""
        return cls(checkbox=value)


class Date(PropertyValue):
    """Notion complex date type - may include timestamp and/or be a date range."""

    __type__ = "date"

    class NestedDate(NestedObject):
        start: Union[date, datetime]
        end: Optional[Union[date, datetime]] = None

    date: NestedDate = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.date is None:
            return None

        if self.date.end is None:
            return f"{self.date.start}"

        return f"{self.date.start} :: {self.date.end}"

    @classmethod
    def from_value(cls, value):
        """Create a new Date from the native value."""
        inner = NestedDate(start=value)
        return cls(date=inner)


class SelectOne(PropertyValue):
    """Notion select type."""

    __type__ = "select"

    select: SelectOption = None

    def __post_init__(self):
        if self.select is None:
            raise ValueError("missing select object")

        if self.select.name is None and self.select.option_id is None:
            raise ValueError('must provide at least one of "name" or "option_id"')

    def __str__(self):
        """Return a string representation of this object."""
        return self.select.name or self.select.option_id or None

    @classmethod
    def from_value(cls, value):
        """Create a new SelectOne from the given string."""
        inner = SelectOption(name=value)
        return cls(select=inner)


class MultiSelect(PropertyValue):
    """Notion multi-select type."""

    __type__ = "multi_select"

    multi_select: List[SelectOption] = []

    def __str__(self):
        """Return a string representation of this object."""
        return ", ".join(self.multi_select)

    @classmethod
    def from_value(cls, value):
        """Create a new SelectOne from the given string."""
        return cls(id=None, name=value, option_id=None)


class People(PropertyValue):
    __type__ = "people"

    people: List[User] = []


class URL(PropertyValue):
    __type__ = "url"

    url: str = None


class Email(PropertyValue):
    __type__ = "email"

    email: str = None


class PhoneNumber(PropertyValue):
    __type__ = "phone_number"

    phone_number: str = None


class FormulaObject(TypedObject):
    pass


class StringFormula(FormulaObject):
    __type__ = "string"

    string: str = None


class NumberFormula(FormulaObject):
    __type__ = "number"

    string: Union[int, float] = None


class DateFormula(FormulaObject):
    __type__ = "date"

    date: Date = None


class Formula(PropertyValue):
    __type__ = "formula"

    formula: FormulaObject = None


class Relation(PropertyValue):
    __type__ = "relation"

    relation: List[str] = []


class CreatedTime(PropertyValue):
    __type__ = "created_time"

    created_time: datetime = None


class CreatedBy(PropertyValue):
    __type__ = "created_by"

    created_by: User = None


class LastEditedTime(PropertyValue):
    __type__ = "last_edited_time"

    last_edited_time: datetime = None


class LastEditedBy(PropertyValue):
    __type__ = "last_edited_by"

    last_edited_by: User = None


class Text(object):
    """Standard Notion text properties."""

    def __init__(self, type, id, text=list()):
        super().__init__(type, id)
        self.text = text

    def __str__(self):
        """Return a string representation of this object."""
        return "".join(str(elem) for elem in self.text)

    def __len__(self):
        """Return the number of elements in the RichText object."""
        return len(self.text)

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        rtf = [elem.to_json() for elem in self.text]
        return super().to_json(**{self.type: rtf})

    @classmethod
    def from_value(cls, value):
        """Create a new Text value from the native string value."""
        rtf = TextObject(text=value)
        return cls(id=None, text=[rtf])


property_type_map = {
    "title": Title,
    "number": Number,
    "date": Date,
    "checkbox": Checkbox,
    "select": SelectOne,
    "rich_text": RichText,
}


def notion_to_python(data):
    """Convert the raw data from Notion to a python object."""
    if data is None:
        return None

    if "type" not in data:
        raise ValueError("unable to determine content type")

    cls = property_type_map.get(data["type"], None)

    if cls is None:
        raise TypeError(f'unsupported data type: {data["type"]}')

    return cls.from_json(data)


def python_to_notion(value, cls):
    """Convert the python object to Notion API data.

    This will raise a TypeError if a conversion is not found.
    """

    # if the given value is already of the expected class type...
    if isinstance(value, cls):
        obj = value

    # otherwise, ask the class to convert from the given value
    else:
        try:
            obj = cls.from_value(value)
        except NotImplementedError:
            raise TypeError(f"Unsupported data type - {cls}")

    return obj.to_json()
