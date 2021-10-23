"""Wrapper for Notion API data types.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from .core import DataObject, NestedObject, TypedObject
from .schema import Function
from .text import Color, FullColor, plain_text
from .user import User

log = logging.getLogger(__name__)


class PageReference(DataObject):
    """A page reference is an object with an id property."""

    id: UUID


class Annotations(DataObject):
    """Style information for RichTextObject's."""

    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: FullColor = None

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


class EmojiObject(TypedObject, type="emoji"):
    """A Notion emoji object."""

    emoji: str = None


class FileObject(TypedObject):
    """A Notion file object."""

    name: Optional[str] = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.name or "_unknown_"


class File(FileObject, type="file"):
    """A Notion file reference."""

    class NestedData(NestedObject):
        url: str = None
        expiry_time: datetime = None

    file: NestedData = None


class ExternalFile(FileObject, type="external"):
    """An external file reference."""

    class NestedData(NestedObject):
        url: str = None

    external: NestedData = None


class DateRange(DataObject):
    """A Notion date range, with an optional end date."""

    start: Union[date, datetime]
    end: Optional[Union[date, datetime]] = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.end is None:
            return f"{self.start}"

        return f"{self.start} :: {self.end}"


class RichTextObject(TypedObject):
    """Base class for Notion rich text elements."""

    plain_text: str
    href: str = None
    annotations: Annotations = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.href is None:
            text = self.plain_text
        else:
            text = f"[{self.plain_text}]({self.href})"

        # TODO add markdown for annotations
        # e.g. something like: text = markup(text, self.annotations)

        return text


class TextObject(RichTextObject, type="text"):
    """Notion text element."""

    class NestedData(NestedObject):
        content: str
        link: LinkObject = None

    text: NestedData = None

    @classmethod
    def from_value(cls, string):
        """Return a TextObject from the native string."""

        # TODO support markdown in the text string

        text = cls.NestedData(content=string)
        return cls(plain_text=string, text=text)


class MentionData(TypedObject):
    pass


class MentionUser(MentionData, type="user"):
    user: User


class MentionPage(MentionData, type="page"):

    page: PageReference


class MentionDatabase(MentionData, type="database"):

    database: PageReference


class MentionDate(MentionData, type="date"):
    date: DateRange


class MentionObject(RichTextObject, type="mention"):
    """Notion mention element."""

    mention: MentionData = None


class Expression(NestedObject):
    expression: str


class EquationObject(RichTextObject, type="equation"):
    """Notion equation element."""

    equation: Expression = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.equation is None:
            return None

        return self.equation.expression


class NativeTypeMixin(object):
    """Mixin class for properties that can be represented as native Python types."""

    def __str__(self):
        """Return a string representation of this object."""

        value = self.Value

        if value is None:
            return ""

        return str(value)

    def __eq__(self, other):
        """Determine if this property is equal to the given object."""

        return self.Value == other

    def __ne__(self, other):
        """Determine if this property is not equal to the given object."""

        return self.Value != other

    @property
    def Value(self):
        """Get the current value of this property as a native Python type."""

        cls = self.__class__

        # check to see if the object has a field with the type-name
        # (this is assigned by TypedObject during subclass creation)
        if hasattr(cls, "type") and hasattr(self, cls.type):
            return getattr(self, cls.type)

        raise NotImplementedError()

    @classmethod
    def from_value(cls, value):
        """Build the property value from the native Python value."""

        # use type-name field to instantiate the class when possible
        if hasattr(cls, "type"):
            return cls(**{cls.type: value})

        raise NotImplementedError()


class PropertyValue(TypedObject):
    """Base class for Notion property values."""

    id: str = None


class Title(NativeTypeMixin, PropertyValue, type="title"):
    """Notion title type."""

    title: List[RichTextObject] = []

    def __len__(self):
        """Return the number of object in the Title object."""

        return len(self.title)

    @property
    def Value(self):
        """Return the plain text from this Title."""

        if self.title is None:
            return None

        return plain_text(*self.title)

    @classmethod
    def from_value(cls, value):
        text = TextObject.from_value(value)
        return cls(title=[text])


class RichText(NativeTypeMixin, PropertyValue, type="rich_text"):
    """Notion rich text type."""

    rich_text: List[RichTextObject] = []

    def __len__(self):
        """Return the number of object in the RichText object."""
        return len(self.rich_text)

    @property
    def Value(self):
        """Return the plain text from this RichText."""

        if self.rich_text is None:
            return None

        return plain_text(*self.rich_text)

    @classmethod
    def from_value(cls, value):
        text = TextObject.from_value(value)
        return cls(rich_text=[text])


class Number(NativeTypeMixin, PropertyValue, type="number"):
    """Simple number type."""

    number: Union[float, int] = None

    def __iadd__(self, other):
        """Add the given value to this Number."""

        self.number += other
        return self

    def __isub__(self, other):
        """Subtract the given value from this Number."""

        self.number -= other
        return self


class Checkbox(NativeTypeMixin, PropertyValue, type="checkbox"):
    """Simple checkbox type; represented as a boolean."""

    checkbox: bool = None


class Date(PropertyValue, type="date"):
    """Notion complex date type - may include timestamp and/or be a date range."""

    date: DateRange = None

    def __contains__(self, other):
        """Determines if the given date is in the range (inclusive) of this Date.

        Raises ValueError if the Date object is not a range - e.g. has no end date.
        """

        if not self.IsRange:
            raise ValueError("This date is not a range")

        return self.Start <= other <= self.End

    def __str__(self):
        if self.date is None:
            return ""

        return str(self.date)

    @property
    def IsRange(self):
        """Indicates if this object represents a date range (versus a single date)."""

        if self.date is None:
            return False

        return self.date.end is not None

    @property
    def Start(self):
        return None if self.date is None else self.date.start

    @property
    def End(self):
        return None if self.date is None else self.date.end

    @classmethod
    def from_value(cls, value):
        """Create a new Date from the native value."""
        inner = DateRange(start=value)
        return cls(date=inner)


class SelectValue(DataObject):
    """Values for select & multi-select properties."""

    name: str
    id: UUID = None
    color: Color = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.name


class SelectOne(NativeTypeMixin, PropertyValue, type="select"):
    """Notion select type."""

    select: SelectValue = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.Value or ""

    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        To avoid confusion, this method only compares Select options by name, not ID.
        """

        if self.select is None:
            return other == None

        return other == self.select.name

    @property
    def Value(self):
        if self.select is None:
            return None

        return str(self.select)

    @classmethod
    def from_value(cls, value):
        return cls(select=SelectValue(name=value))


class MultiSelect(PropertyValue, type="multi_select"):
    """Notion multi-select type."""

    multi_select: List[SelectValue] = []

    def __str__(self):
        """Return a string representation of this object."""
        return ", ".join(self.Values)

    def __iadd__(self, other):
        """Add the given option to this MultiSelect."""

        if other is None:
            raise ValueError(f"'None' is invalid for this property")

        if other in self:
            raise ValueError(f"Item already selected: {other}")

        opt = SelectValue(name=other)
        self.multi_select.append(opt)

        return self

    def __isub__(self, other):
        """Remove the given value from this MultiSelect."""

        self.multi_select = [opt for opt in self.multi_select if opt.name != other]

        return self

    def __contains__(self, name):
        """Determines if the given name is in this MultiSelect.

        To avoid confusion, only names are considered for comparison, not ID's.
        """

        for opt in self.multi_select:
            if opt.name == name:
                return True

        return False

    def __iter__(self):
        return self.Values

    @property
    def Values(self):
        """Return the names of each value in this MultiSelect as a list."""

        if self.multi_select is None:
            return None

        return [str(val) for val in self.multi_select if val.name is not None]

    @classmethod
    def from_values(cls, *values):
        """Initialize a new MultiSelect from the list of values.

        All values in the list will be converted to strings.
        """

        return cls(
            multi_select=[
                SelectValue(name=str(val)) for val in values if val is not None
            ]
        )


class People(PropertyValue, type="people"):
    """Notion people type."""

    people: List[User] = []

    def __iter__(self):
        """Iterates over the User's in this property."""

        if self.people is None:
            return None

        return iter(self.people)

    def __contains__(self, other):
        """Determines if the given User or name is in this People.

        To avoid confusion, only names are considered for comparison (not ID's).
        """

        for user in self.people:
            if user == other:
                return True
            elif user.name == other:
                return True

        return False

    def __str__(self):
        return ", ".join([str(user) for user in self.people])


class URL(NativeTypeMixin, PropertyValue, type="url"):
    """Notion URL type."""

    url: str = None


class Email(NativeTypeMixin, PropertyValue, type="email"):
    """Notion email type."""

    email: str = None


class PhoneNumber(NativeTypeMixin, PropertyValue, type="phone_number"):
    """Notion phone type."""

    phone_number: str = None


class Files(PropertyValue, type="files"):
    """Notion files type."""

    files: List[FileObject] = []

    def __contains__(self, other):
        """Determines if the given FileObject or name is in the file list.

        To avoid confusion, only names are considered for comparison.
        """

        if self.files is None:
            return False

        for file in self.files:
            if file == other:
                return True
            elif file.name == other:
                return True

        return False

    def __str__(self):
        return "; ".join([str(file) for file in self.files])


class FormulaResult(TypedObject):
    """A Notion formula result.

    This object contains the result of the expression in the database properties.
    """

    def __str__(self):
        return self.Result or ""

    @property
    def Result(self):
        """Return the result of this FormulaResult."""

        raise NotImplemented("Result unavailable")


class StringFormula(FormulaResult, type="string"):
    """A Notion string formula result."""

    string: str = None

    @property
    def Result(self):
        """Return the result of this StringFormula."""

        return self.string


class NumberFormula(FormulaResult, type="number"):
    """A Notion number formula result."""

    number: Union[float, int] = None

    @property
    def Result(self):
        """Return the result of this NumberFormula."""

        return self.number


class DateFormula(FormulaResult, type="date"):
    """A Notion date formula result."""

    date: DateRange = None

    @property
    def Result(self):
        """Return the result of this DateFormula."""

        return self.date


class Formula(PropertyValue, type="formula"):
    """A Notion formula property value."""

    formula: FormulaResult = None

    def __str__(self):
        return str(self.Result or "")

    @property
    def Result(self):
        """Return the result of this Formula in its native type."""

        if self.formula is None:
            return None

        return self.formula.Result


class Relation(PropertyValue, type="relation"):
    """A Notion relation property value."""

    relation: List[PageReference] = []


class RollupObject(TypedObject):
    """A Notion rollup property value."""

    function: Function


class RollupNumber(RollupObject, type="number"):
    """A Notion rollup number property value."""

    number: Union[float, int] = None


class RollupDate(RollupObject, type="date"):
    """A Notion rollup date property value."""

    date: DateRange = None


class RollupArray(RollupObject, type="array"):
    """A Notion rollup array property value."""

    array: List[PropertyValue] = None


class Rollup(PropertyValue, type="rollup"):
    """A Notion rollup property value."""

    rollup: RollupObject


class CreatedTime(NativeTypeMixin, PropertyValue, type="created_time"):
    """A Notion created-time property value."""

    created_time: datetime = None


class CreatedBy(PropertyValue, type="created_by"):
    """A Notion created-by property value."""

    created_by: User = None

    def __str__(self):
        return str(self.created_by)


class LastEditedTime(NativeTypeMixin, PropertyValue, type="last_edited_time"):
    """A Notion last-edited-time property value."""

    last_edited_time: datetime = None


class LastEditedBy(PropertyValue, type="last_edited_by"):
    """A Notion last-edited-by property value."""

    last_edited_by: User = None

    def __str__(self):
        return str(self.last_edited_by)
