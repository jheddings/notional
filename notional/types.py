"""Wrapper for Notion API data types.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

import logging
from datetime import date, datetime
from typing import List, Optional, Union
from uuid import UUID

from .core import DataObject, NestedObject, TypedObject
from .schema import Function
from .text import Color, RichTextObject, TextObject, plain_text
from .user import User

log = logging.getLogger(__name__)


class PageReference(DataObject):
    """A page reference is an object with an id property."""

    id: UUID


class EmojiObject(TypedObject, type="emoji"):
    """A Notion emoji object."""

    emoji: str


class FileObject(TypedObject):
    """A Notion file object.

    Depending on the context, a FileObject may require a name (such as in the `Files`
    property).  This makes the object heirarchy difficult, so here we simply allow
    `name` to be optional.  It is the responsibility of the caller to set `name` if
    required by the API.
    """

    name: Optional[str] = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.name or "__unknown__"


class HostedFile(FileObject, type="file"):
    """A Notion file object."""

    class NestedData(NestedObject):
        url: str
        expiry_time: Optional[datetime] = None

    file: Optional[NestedData] = None


class ExternalFile(FileObject, type="external"):
    """An external file object."""

    class NestedData(NestedObject):
        url: str

    external: Optional[NestedData] = None

    @classmethod
    def from_url(cls, url):
        data = cls.NestedData(url=url)
        return cls(external=data)


class DateRange(DataObject):
    """A Notion date range, with an optional end date."""

    start: Union[date, datetime]
    end: Optional[Union[date, datetime]] = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.end is None:
            return f"{self.start}"

        return f"{self.start} :: {self.end}"


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


class MentionLink(MentionData, type="link_preview"):
    url: str


class MentionTemplateData(TypedObject):
    pass


class MentionTemplateDate(MentionTemplateData, type="template_mention_date"):
    template_mention_date: str


class MentionTemplateUser(MentionTemplateData, type="template_mention_user"):
    template_mention_user: str


class MentionTemplate(MentionData, type="template_mention"):
    template_mention: MentionTemplateData


class MentionObject(RichTextObject, type="mention"):
    """Notion mention element."""

    mention: MentionData


class Expression(NestedObject):
    expression: str


class EquationObject(RichTextObject, type="equation"):
    """Notion equation element."""

    equation: Expression

    def __str__(self):
        """Return a string representation of this object."""

        if self.equation is None:
            return None

        return self.equation.expression


class NativeTypeMixin:
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

    id: Optional[str] = None


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
    def from_value(cls, *strings):

        text = []

        for string in strings:
            if string is None:
                continue

            text.append(TextObject.from_value(string))

        return cls(title=text)


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
    def from_value(cls, *strings):

        text = []

        for string in strings:
            if string is None:
                continue

            text.append(TextObject.from_value(string))

        return cls(rich_text=text)


class Number(NativeTypeMixin, PropertyValue, type="number"):
    """Simple number type."""

    number: Optional[Union[float, int]] = None

    def __iadd__(self, other):
        """Add the given value to this Number."""

        self.number += other
        return self

    def __isub__(self, other):
        """Subtract the given value from this Number."""

        self.number -= other
        return self

    @property
    def Value(self):
        """Get the current value of this property as a native Python number."""

        if self.number is None:
            return None

        if self.number == int(self.number):
            return int(self.number)

        return self.number


class Checkbox(NativeTypeMixin, PropertyValue, type="checkbox"):
    """Simple checkbox type; represented as a boolean."""

    checkbox: Optional[bool] = None


class Date(PropertyValue, type="date"):
    """Notion complex date type - may include timestamp and/or be a date range."""

    date: Optional[DateRange] = None

    def __contains__(self, other):
        """Determines if the given date is in the range (inclusive) of this Date.

        Raises ValueError if the Date object is not a range - e.g. has no end date.
        """

        if not self.IsRange:
            raise ValueError("This date is not a range")

        return self.Start <= other <= self.End

    def __str__(self):
        return "" if self.date is None else str(self.date)

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

        if value is None:
            inner = DateRange(start=None)
        else:
            inner = DateRange(start=value)

        return cls(date=inner)


class SelectValue(DataObject):
    """Values for select & multi-select properties."""

    name: str
    id: Optional[Union[UUID, str]] = None
    color: Optional[Color] = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.name


class SelectOne(NativeTypeMixin, PropertyValue, type="select"):
    """Notion select type."""

    select: Optional[SelectValue] = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.Value or ""

    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        To avoid confusion, this method only compares Select options by name, not ID.
        """

        if self.select is None:
            return other is None

        return other == self.select.name

    @property
    def Value(self):
        if self.select is None:
            return None

        return str(self.select)

    @classmethod
    def from_value(cls, value):

        if value is None:
            return cls(select={})

        return cls(select=SelectValue(name=value))


class MultiSelect(PropertyValue, type="multi_select"):
    """Notion multi-select type."""

    multi_select: List[SelectValue] = []

    def __str__(self):
        """Return a string representation of this object."""
        return ", ".join(self.Values)

    def __len__(self):
        """Counts the number of selected values."""
        return len(self.multi_select)

    def __iadd__(self, other):
        """Add the given option to this MultiSelect."""

        if other in self:
            raise ValueError(f"Duplicate item: {other}")

        return self.append(other)

    def __isub__(self, other):
        """Remove the given value from this MultiSelect."""

        if other not in self:
            raise ValueError(f"No such item: {other}")

        return self.remove(other)

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

    def append(self, *values):
        """Add selected values to this MultiSelect."""

        for value in values:
            if value is None:
                raise ValueError("'None' is an invalid value")

            if value not in self:
                opt = SelectValue(name=value)
                self.multi_select.append(opt)

        return self

    def remove(self, *values):
        """Removed selected values from this MultiSelect."""

        self.multi_select = [opt for opt in self.multi_select if opt.name not in values]

        return self

    @property
    def Values(self):
        """Return the names of each value in this MultiSelect as a list."""

        if self.multi_select is None:
            return None

        return [str(val) for val in self.multi_select if val.name is not None]

    @classmethod
    def from_value(cls, value):
        """Initialize a new MultiSelect from the given value."""

        if isinstance(value, list):
            return cls.from_values(*value)

        return cls.from_values(value)

    @classmethod
    def from_values(cls, *values):
        """This method accepts a list of values, converting them into SelectOption's.

        All values in the list will be automatically converted to strings.
        """

        select = []

        for value in values:
            if value is None:
                continue

            select.append(SelectValue(name=str(value)))

        return cls(multi_select=select)


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

            if user.name == other:
                return True

        return False

    def __str__(self):
        return ", ".join([str(user) for user in self.people])


class URL(NativeTypeMixin, PropertyValue, type="url"):
    """Notion URL type."""

    url: Optional[str] = None


class Email(NativeTypeMixin, PropertyValue, type="email"):
    """Notion email type."""

    email: Optional[str] = None


class PhoneNumber(NativeTypeMixin, PropertyValue, type="phone_number"):
    """Notion phone type."""

    phone_number: Optional[str] = None


class Files(PropertyValue, type="files"):
    """Notion files type."""

    files: List[FileObject] = []

    def __contains__(self, other):
        """Determines if the given FileObject or name is in the property."""

        if self.files is None:
            return False

        for ref in self.files:
            if ref == other:
                return True

            if ref.name == other:
                return True

        return False

    def __str__(self):
        return "; ".join([str(file) for file in self.files])

    def __iadd__(self, ref):
        if ref in self:
            raise ValueError(f"Item exists: {ref}")

        self.append(ref)
        return self

    def __isub__(self, ref):
        if ref not in self:
            raise ValueError(f"No such item: {ref}")

        self.remove(ref)
        return self

    def append(self, ref):
        log.debug("append file - %s", ref)
        self.files.append(ref)

    def remove(self, ref):
        log.debug("remove file - %s", ref)
        self.files.remove(ref)


class FormulaResult(TypedObject):
    """A Notion formula result.

    This object contains the result of the expression in the database properties.
    """

    def __str__(self):
        return self.Result or ""

    @property
    def Result(self):
        """Return the result of this FormulaResult."""

        raise NotImplementedError("Result unavailable")


class StringFormula(FormulaResult, type="string"):
    """A Notion string formula result."""

    string: Optional[str] = None

    @property
    def Result(self):
        """Return the result of this StringFormula."""

        return self.string


class NumberFormula(FormulaResult, type="number"):
    """A Notion number formula result."""

    number: Optional[Union[float, int]] = None

    @property
    def Result(self):
        """Return the result of this NumberFormula."""

        return self.number


class DateFormula(FormulaResult, type="date"):
    """A Notion date formula result."""

    date: Optional[DateRange] = None

    @property
    def Result(self):
        """Return the result of this DateFormula."""

        return self.date


class Formula(PropertyValue, type="formula"):
    """A Notion formula property value."""

    formula: Optional[FormulaResult] = None

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

    function: Optional[Function] = None


class RollupNumber(RollupObject, type="number"):
    """A Notion rollup number property value."""

    number: Optional[Union[float, int]] = None


class RollupDate(RollupObject, type="date"):
    """A Notion rollup date property value."""

    date: Optional[DateRange] = None


class RollupArray(RollupObject, type="array"):
    """A Notion rollup array property value."""

    array: List[PropertyValue]


class Rollup(PropertyValue, type="rollup"):
    """A Notion rollup property value."""

    rollup: Optional[RollupObject] = None


class CreatedTime(NativeTypeMixin, PropertyValue, type="created_time"):
    """A Notion created-time property value."""

    created_time: datetime


class CreatedBy(PropertyValue, type="created_by"):
    """A Notion created-by property value."""

    created_by: User

    def __str__(self):
        return str(self.created_by)


class LastEditedTime(NativeTypeMixin, PropertyValue, type="last_edited_time"):
    """A Notion last-edited-time property value."""

    last_edited_time: datetime


class LastEditedBy(PropertyValue, type="last_edited_by"):
    """A Notion last-edited-by property value."""

    last_edited_by: User

    def __str__(self):
        return str(self.last_edited_by)
