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
            text = self.plain_text
        else:
            text = f"[{self.plain_text}]({self.href})"

        # TODO add markdown for annotations
        # e.g. something like: text = markup(text, self.annotations)

        return text


class TextObject(RichTextObject, type="text"):
    """Notion text element."""

    class NestedText(NestedObject):
        content: str
        link: LinkObject = None

    text: NestedText = None

    @classmethod
    def from_str(cls, string):
        """Return a TextObject from the native string."""

        # TODO support markdown in the text string

        text = cls.NestedText(content=string)
        return cls(plain_text=string, text=text)


class MentionPageRef(DataObject):
    id: str


class MentionObject(RichTextObject, type="mention"):
    """Notion mention element."""

    class NestedMention(NestedObject, TypedObject):
        pass

    class MentionUser(NestedMention):
        user: User

    class MentionPage(NestedMention):
        page: MentionPageRef

    class MentionDatabase(NestedMention):
        database: MentionPageRef

    mention: NestedMention = None


class EquationObject(RichTextObject, type="equation"):
    """Notion equation element."""

    class NestedEquation(NestedObject):
        expression: str

    equation: NestedEquation = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.equation is None:
            return None

        return self.equation.expression


class NativeTypeMixin(object):
    """Mixin class for properties that can be represented as native Python types."""

    def __str__(self):
        """Return a string representation of this object."""

        return str(self.Value or "")

    def __eq__(self, other):
        """Determine if this property is equal to the given object."""

        return self.Value == other

    def __ne__(self, other):
        """Determine if this property is not equal to the given object."""

        return self.Value != other

    @property
    def Value(self):
        raise NotImplementedError()

    @Value.setter
    def Value(self, value):
        raise NotImplementedError()


class PropertyValue(TypedObject):
    """Base class for Notion property values."""

    id: str = None


class Title(PropertyValue, NativeTypeMixin, type="title"):
    """Notion title type."""

    # TODO figure out how to combine with RichText

    title: List[RichTextObject] = []

    def __len__(self):
        """Return the number of object in the Title object."""

        return len(self.title)

    @property
    def Value(self):
        """Return the plain text from this Title."""

        if self.title is None:
            return None

        return "".join(str(text) for text in self.title)

    @Value.setter
    def Value(self, value):
        self.title = [TextObject.from_str(value)]


class RichText(PropertyValue, NativeTypeMixin, type="rich_text"):
    """Notion rich text type."""

    # TODO figure out how to combine with Title

    rich_text: List[RichTextObject] = []

    def __len__(self):
        """Return the number of object in the RichText object."""

        return len(self.rich_text)

    @property
    def Value(self):
        """Return the plain text from this RichText."""

        if self.rich_text is None:
            return None

        return "".join(str(text) for text in self.rich_text)

    @Value.setter
    def Value(self, value):
        self.rich_text = [TextObject.from_str(value)]


class Number(PropertyValue, NativeTypeMixin, type="number"):
    """Simple number type."""

    number: Union[int, float] = None

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
        return self.number

    @Value.setter
    def Value(self, value):
        self.number = value


class Checkbox(PropertyValue, NativeTypeMixin, type="checkbox"):
    """Simple checkbox type; represented as a boolean."""

    checkbox: bool = None

    @property
    def Value(self):
        return self.checkbox

    @Value.setter
    def Value(self, value):
        self.checkbox = value


class DateRange(DataObject):
    """A Notion date range, with an optional end date."""

    start: Union[date, datetime]
    end: Optional[Union[date, datetime]] = None


class Date(PropertyValue, type="date"):
    """Notion complex date type - may include timestamp and/or be a date range."""

    date: DateRange = None

    def __str__(self):
        """Return a string representation of this object."""

        if self.date is None:
            return None

        if self.date.end is None:
            return f"{self.date.start}"

        return f"{self.date.start} :: {self.date.end}"

    def __contains__(self, other):
        """Determines if the given date is in the range (inclusive) of this Date.

        Raises ValueError if the Date object is not a range - e.g. has no end date.
        """

        if not self.IsRange:
            raise ValueError("This date is not a range")

        return self.Start <= other <= self.End

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
        inner = NestedDate(start=value)
        return cls(date=inner)


class SelectOne(PropertyValue, NativeTypeMixin, type="select"):
    """Notion select type."""

    select: SelectOption = None

    def __str__(self):
        """Return a string representation of this object."""

        return self.select.name or self.select.option_id or ""

    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        To avoid confusion, this method only compares Select options by name, not ID.
        """

        if self.select is None:
            return other == None

        return other == self.select.name

    @property
    def Value(self):
        """Return the value of the Select option as either the name or ID."""

        return self.select.name or self.select.option_id or None

    @Value.setter
    def Value(self, value):
        self.select = SelectOption(name=value)


class MultiSelect(PropertyValue, type="multi_select"):
    """Notion multi-select type."""

    multi_select: List[SelectOption] = []

    def __str__(self):
        """Return a string representation of this object."""
        return ", ".join(self.Values)

    def __iadd__(self, other):
        """Add the given option to this MultiSelect."""

        if other in self:
            raise ValueError(f"Item already selected: {other}")

        opt = SelectOption(name=other)
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

    @property
    def Values(self):
        """Return the values of this MultiSelect as either names or ID's."""

        # TODO don't return None values
        return [select.name or select.id for select in self.multi_select]


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


class URL(PropertyValue, type="url"):
    """Notion URL type."""

    url: str = None


class Email(PropertyValue, type="email"):
    """Notion email type."""

    email: str = None


class PhoneNumber(PropertyValue, type="phone_number"):
    """Notion phone type."""

    phone_number: str = None


class FileRef(DataObject):
    """A Notion file reference."""

    name: str


class Files(PropertyValue, type="files"):
    """Notion files type."""

    files: List[FileRef] = []

    def __contains__(self, other):
        """Determines if the given FileRef or name is in the file list.

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


class FormulaResult(TypedObject):
    """A Notion formula result.

    This object contains the result of the expression in the database properties.
    """

    @property
    def Result(self):
        """Return the result of this FormulaResult."""

        raise NotImplemented("Result unavailable")


class StringFormula(FormulaResult, type="string"):
    """A Notion string formula result."""

    string: str = None

    def __str__(self):
        return self.string or ""

    @property
    def Result(self):
        """Return the result of this StringFormula."""

        return self.string


class NumberFormula(FormulaResult, type="number"):
    """A Notion number formula result."""

    number: Union[int, float] = None

    def __str__(self):
        return str(self.number or "")

    @property
    def Result(self):
        """Return the result of this NumberFormula."""

        return self.number


class DateFormula(FormulaResult, type="date"):
    """A Notion date formula result."""

    date: DateRange = None

    def __str__(self):
        return str(self.date or "")

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

    relation: List[str] = []


class CreatedTime(PropertyValue, type="created_time"):
    """A Notion created-time property value."""

    created_time: datetime = None


class CreatedBy(PropertyValue, type="created_by"):
    """A Notion created-by property value."""

    created_by: User = None


class LastEditedTime(PropertyValue, type="last_edited_time"):
    """A Notion last-edited-time property value."""

    last_edited_time: datetime = None


class LastEditedBy(PropertyValue, type="last_edited_by"):
    """A Notion last-edited-by property value."""

    last_edited_by: User = None
