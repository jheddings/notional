"""Wrapper for Notion API data types.

Similar to other records, these object provide access to the primitive data structure
used in the Notion API as well as higher-level methods.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Literal, Optional, Union
from uuid import UUID

from notion_client import helpers

from . import util
from .core import DataObject, NotionObject, TypedObject
from .schema import Function
from .text import Color, RichTextObject, plain_text, rich_text
from .user import Person, User


class ObjectReference(NotionObject, ABC):
    """A general-purpose object reference in the Notion API."""

    id: UUID

    @classmethod
    def __compose__(cls, ref: Union[str, UUID, "ParentRef", NotionObject]):
        """Compose an ObjectReference from the given reference.

        Strings may be either UUID's or URL's to Notion content.
        """

        if isinstance(ref, cls):
            return ref.model_copy(deep=True)

        if isinstance(ref, ParentRef):
            # ParentRef's are typed-objects with a nested UUID
            return ObjectReference(id=ref())

        if isinstance(ref, NotionObject) and hasattr(ref, "id"):
            # re-compose the ObjectReference from the internal ID
            return ObjectReference[ref.id]

        if isinstance(ref, UUID):
            return ObjectReference(id=ref)

        if isinstance(ref, str):
            ref = util.extract_id_from_string(ref)

            if ref is not None:
                return ObjectReference(id=UUID(ref))

        raise ValueError("Unrecognized 'ref' attribute")

    @property
    def URL(self) -> str:
        """Return the Notion URL for this object reference.

        Note: this is a convenience property only.  It does not guarantee that the
        URL exists or that it is accessible by the integration.
        """
        return helpers.get_url(self.id.hex)


# https://developers.notion.com/reference/parent-object
class ParentRef(TypedObject, ABC):
    """Reference another block as a parent."""

    # note that this class is simply a placeholder for the typed concrete *Ref classes
    # callers should always instantiate the intended concrete versions


class DatabaseRef(ParentRef):
    """Reference a database."""

    database_id: UUID
    type: Literal["database_id"] = "database_id"

    @classmethod
    def __compose__(cls, db_ref: Union[str, UUID, DataObject]):
        """Compose a DatabaseRef from the given reference object."""
        ref = ObjectReference[db_ref]
        return DatabaseRef(database_id=ref.id)


class PageRef(ParentRef):
    """Reference a page."""

    page_id: UUID
    type: Literal["page_id"] = "page_id"

    @classmethod
    def __compose__(cls, page_ref: Union[str, UUID, DataObject]):
        """Compose a PageRef from the given reference object."""
        ref = ObjectReference[page_ref]
        return PageRef(page_id=ref.id)


class BlockRef(ParentRef):
    """Reference a block."""

    block_id: UUID
    type: Literal["block_id"] = "block_id"

    @classmethod
    def __compose__(cls, block_ref: Union[str, UUID, DataObject]):
        """Compose a BlockRef from the given reference object."""
        ref = ObjectReference[block_ref]
        return BlockRef(block_id=ref.id)


class WorkspaceRef(ParentRef):
    """Reference the workspace."""

    workspace: bool = True
    type: Literal["workspace"] = "workspace"


class EmojiObject(TypedObject):
    """A Notion emoji object."""

    emoji: str
    type: Literal["emoji"] = "emoji"

    def __str__(self) -> str:
        """Return this EmojiObject as a simple string."""
        return self.emoji

    @classmethod
    def __compose__(cls, emoji):
        """Compose an EmojiObject from the given emoji string."""
        return EmojiObject(emoji=emoji)


class FileObject(TypedObject, ABC):
    """A Notion file object.

    Depending on the context, a FileObject may require a name (such as in the `Files`
    property).  This makes the object hierarchy difficult, so here we simply allow
    `name` to be optional.  It is the responsibility of the caller to set `name` if
    required by the API.
    """

    name: Optional[str] = None

    def __str__(self) -> str:
        """Return a string representation of this object."""
        return self.name or "__unknown__"

    @property
    def URL(self):
        """Return the URL to this FileObject."""
        return self("url")


class HostedFile(FileObject):
    """A Notion file object."""

    class _NestedData(NotionObject):
        url: str
        expiry_time: Optional[datetime] = None

    file: _NestedData
    type: Literal["file"] = "file"


class ExternalFile(FileObject):
    """An external file object."""

    class _NestedData(NotionObject):
        url: str

    external: _NestedData
    type: Literal["external"] = "external"

    def __str__(self) -> str:
        """Return a string representation of this object."""
        name = super().__str__()

        if self.external and self.external.url:
            return f"![{name}]({self.external.url})"

        return name

    @classmethod
    def __compose__(cls, url, name=None):
        """Create a new `ExternalFile` from the given URL."""
        return cls(name=name, external=cls._NestedData(url=url))


class DateRange(NotionObject):
    """A Notion date range, with an optional end date."""

    start: Union[date, datetime]
    end: Optional[Union[date, datetime]] = None

    def __str__(self) -> str:
        """Return a string representation of this object."""

        if self.end is None:
            return f"{self.start}"

        return f"{self.start} :: {self.end}"


class MentionData(TypedObject, ABC):
    """Base class for typed `Mention` data objects."""


class MentionUser(MentionData):
    """Nested user data for `Mention` properties."""

    user: User
    type: Literal["user"] = "user"

    @classmethod
    def __compose__(cls, user: User):
        """Build a `Mention` object for the specified user.

        The `id` field must be set for the given User.  Other fields may cause errors
        if they do not match the specific type returned from the API.
        """

        return MentionObject(plain_text=str(user), mention=MentionUser(user=user))


class MentionPage(MentionData):
    """Nested page data for `Mention` properties."""

    page: ObjectReference
    type: Literal["page"] = "page"

    @classmethod
    def __compose__(cls, page_ref):
        """Build a `Mention` object for the specified page reference."""

        ref = ObjectReference[page_ref]

        return MentionObject(plain_text=str(ref), mention=MentionPage(page=ref))


class MentionDatabase(MentionData):
    """Nested database information for `Mention` properties."""

    database: ObjectReference
    type: Literal["database"] = "database"

    @classmethod
    def __compose__(cls, page):
        """Build a `Mention` object for the specified database reference."""

        ref = ObjectReference[page]

        return MentionObject(plain_text=str(ref), mention=MentionDatabase(database=ref))


class MentionDate(MentionData):
    """Nested date data for `Mention` properties."""

    date: DateRange
    type: Literal["date"] = "date"

    @classmethod
    def __compose__(cls, start, end=None):
        """Build a `Mention` object for the specified URL."""

        date_obj = DateRange(start=start, end=end)

        return MentionObject(
            plain_text=str(date_obj), mention=MentionDate(date=date_obj)
        )


class MentionLinkPreview(MentionData):
    """Nested url data for `Mention` properties.

    These objects cannot be created via the API.
    """

    class _NestedData(NotionObject):
        url: str

    link_preview: _NestedData
    type: Literal["link_preview"] = "link_preview"


class MentionTemplateData(TypedObject, ABC):
    """Nested template data for `Mention` properties."""


class MentionTemplateDate(MentionTemplateData):
    """Nested date template data for `Mention` properties."""

    template_mention_date: str
    type: Literal["template_mention_date"] = "template_mention_date"


class MentionTemplateUser(MentionTemplateData):
    """Nested user template data for `Mention` properties."""

    template_mention_user: str
    type: Literal["template_mention_user"] = "template_mention_user"


class MentionTemplate(MentionData):
    """Nested template data for `Mention` properties."""

    template_mention: MentionTemplateData
    type: Literal["template_mention"] = "template_mention"


class MentionObject(RichTextObject):
    """Notion mention element."""

    mention: MentionData
    type: Literal["mention"] = "mention"


class EquationObject(RichTextObject):
    """Notion equation element."""

    class _NestedData(NotionObject):
        expression: str

    equation: _NestedData
    type: Literal["equation"] = "equation"

    def __str__(self) -> str:
        """Return a string representation of this object."""

        if self.equation is None:
            return None

        return self.equation.expression


class NativeTypeMixin:
    """Mixin class for properties that can be represented as native Python types."""

    def __str__(self) -> str:
        """Return a string representation of this object."""

        value = self.Value

        if value is None:
            return ""

        return str(value)

    def __eq__(self, other):
        """Determine if this property is equal to the given object."""

        # if `other` is a NativeTypeMixin, this comparrison will call __eq__ on that
        # object using this objects `Value` as the value for `other` (allowing callers
        # to compare using either native types or NativeTypeMixin's)

        return other == self.Value

    def __ne__(self, other):
        """Determine if this property is not equal to the given object."""
        return not self.__eq__(other)

    @classmethod
    def __compose__(cls, value):
        """Build the property value from the native Python value."""

        attr = cls.model_fields.get("type", None)

        if attr is None:
            raise AttributeError(name="type")

        type = attr.default

        if type is None:
            raise AttributeError(name=attr)

        return cls(**{type: value})

    @property
    def Value(self):
        """Get the current value of this property as a native Python type."""

        attr = getattr(self, "type", None)

        if attr is None:
            raise AttributeError(name="type")

        value = getattr(self, attr, ...)

        if value is Ellipsis:
            raise AttributeError(name=attr)

        return value


class PropertyValue(TypedObject, ABC):
    """Base class for Notion property values."""

    id: Optional[str] = None


class Title(PropertyValue, NativeTypeMixin):
    """Notion title type."""

    title: List[RichTextObject] = []
    type: Literal["title"] = "title"

    def __len__(self):
        """Return the number of object in the Title object."""

        return len(self.title)

    @classmethod
    def __compose__(cls, *text):
        """Create a new `Title` property from the given text elements."""
        return cls(title=rich_text(*text))

    @property
    def Value(self):
        """Return the plain text from this Title."""

        if self.title is None:
            return None

        return plain_text(*self.title)


class RichText(PropertyValue, NativeTypeMixin):
    """Notion rich text type."""

    rich_text: List[RichTextObject] = []
    type: Literal["rich_text"] = "rich_text"

    def __len__(self):
        """Return the number of object in the RichText object."""
        return len(self.rich_text)

    @classmethod
    def __compose__(cls, *text):
        """Create a new `RichText` property from the given strings."""
        return cls(rich_text=rich_text(*text))

    @property
    def Value(self):
        """Return the plain text from this RichText."""

        if self.rich_text is None:
            return None

        return plain_text(*self.rich_text)


class Number(PropertyValue, NativeTypeMixin):
    """Simple number type."""

    number: Optional[Union[float, int]] = None
    type: Literal["number"] = "number"

    def __float__(self):
        """Return the Number as a `float`."""

        if self.number is None:
            raise ValueError("Cannot convert 'None' to float")

        return float(self.number)

    def __int__(self):
        """Return the Number as an `int`."""

        if self.number is None:
            raise ValueError("Cannot convert 'None' to int")

        return int(self.number)

    def __iadd__(self, other):
        """Add the given value to this Number."""

        if isinstance(other, Number):
            self.number += other.Value
        else:
            self.number += other

        return self

    def __isub__(self, other):
        """Subtract the given value from this Number."""

        if isinstance(other, Number):
            self.number -= other.Value
        else:
            self.number -= other

        return self

    def __add__(self, other):
        """Add the value of `other` and returns the result as a Number."""
        return Number[other + self.Value]

    def __sub__(self, other):
        """Subtract the value of `other` and returns the result as a Number."""
        return Number[self.Value - float(other)]

    def __mul__(self, other):
        """Multiply the value of `other` and returns the result as a Number."""
        return Number[other * self.Value]

    def __le__(self, other):
        """Return `True` if this `Number` is less-than-or-equal-to `other`."""
        return self < other or self == other

    def __lt__(self, other):
        """Return `True` if this `Number` is less-than `other`."""
        return other > self.Value

    def __ge__(self, other):
        """Return `True` if this `Number` is greater-than-or-equal-to `other`."""
        return self > other or self == other

    def __gt__(self, other):
        """Return `True` if this `Number` is greater-than `other`."""
        return other < self.Value

    @property
    def Value(self):
        """Get the current value of this property as a native Python number."""
        return self.number


class Checkbox(PropertyValue, NativeTypeMixin):
    """Simple checkbox type; represented as a boolean."""

    checkbox: Optional[bool] = None
    type: Literal["checkbox"] = "checkbox"


class Date(PropertyValue):
    """Notion complex date type - may include timestamp and/or be a date range."""

    date: Optional[DateRange] = None
    type: Literal["date"] = "date"

    def __contains__(self, other):
        """Determine if the given date is in the range (inclusive) of this Date.

        Raises ValueError if the Date object is not a range - e.g. has no end date.
        """

        if not self.IsRange:
            raise ValueError("This date is not a range")

        return self.Start <= other <= self.End

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return "" if self.date is None else str(self.date)

    @classmethod
    def __compose__(cls, start, end=None):
        """Create a new Date from the native values."""
        return cls(date=DateRange(start=start, end=end))

    @property
    def IsRange(self):
        """Determine if this object represents a date range (versus a single date)."""

        if self.date is None:
            return False

        return self.date.end is not None

    @property
    def Start(self):
        """Return the start date of this property."""
        return None if self.date is None else self.date.start

    @property
    def End(self):
        """Return the end date of this property."""
        return None if self.date is None else self.date.end


class Status(PropertyValue, NativeTypeMixin):
    """Notion status property."""

    class _NestedData(NotionObject):
        name: str
        id: Optional[Union[UUID, str]] = None
        color: Optional[Color] = None

    status: Optional[_NestedData] = None
    type: Literal["status"] = "status"

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return self.Value or ""

    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        To avoid confusion, this method compares Status options by name.
        """

        if other is None:
            return self.status is None

        if isinstance(other, Status):
            return self.status.name == other.status.name

        return self.status.name == other

    @classmethod
    def __compose__(cls, name, color=None):
        """Create a `Status` property from the given name.

        :param name: a string to use for this property
        :param color: an optional Color for the status
        """

        if name is None:
            raise ValueError("'name' cannot be None")

        return cls(status=Status._NestedData(name=name, color=color))

    @property
    def Value(self):
        """Return the value of this property as a string."""

        return self.status.name


class SelectValue(NotionObject):
    """Values for select & multi-select properties."""

    name: str
    id: Optional[Union[UUID, str]] = None
    color: Optional[Color] = None

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return self.name

    @classmethod
    def __compose__(cls, value, color=None):
        """Create a `SelectValue` property from the given value.

        :param value: a string to use for this property
        :param color: an optional Color for the value
        """
        return cls(name=value, color=color)


class SelectOne(PropertyValue, NativeTypeMixin):
    """Notion select type."""

    select: Optional[SelectValue] = None
    type: Literal["select"] = "select"

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return self.Value or ""

    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        To avoid confusion, this method compares Select options by name.
        """

        if other is None:
            return self.select is None

        return other == self.select.name

    @classmethod
    def __compose__(cls, value, color=None):
        """Create a `SelectOne` property from the given value.

        :param value: a string to use for this property
        :param color: an optional Color for the value
        """
        return cls(select=SelectValue[value, color])

    @property
    def Value(self):
        """Return the value of this property as a string."""

        if self.select is None:
            return None

        return str(self.select)


class MultiSelect(PropertyValue):
    """Notion multi-select type."""

    multi_select: List[SelectValue] = []
    type: Literal["multi_select"] = "multi_select"

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return ", ".join(self.Values)

    def __len__(self):
        """Count the number of selected values."""
        return len(self.multi_select)

    def __getitem__(self, index):
        """Return the SelectValue object at the given index."""

        if self.multi_select is None:
            raise IndexError("empty property")

        if index > len(self.multi_select):
            raise IndexError("index out of range")

        return self.multi_select[index]

    def __iadd__(self, other):
        """Add the given option to this MultiSelect."""

        if other in self:
            raise ValueError(f"Duplicate item: {other}")

        self.append(other)

        return self

    def __isub__(self, other):
        """Remove the given value from this MultiSelect."""

        if other not in self:
            raise ValueError(f"No such item: {other}")

        self.remove(other)

        return self

    def __contains__(self, name):
        """Determine if the given name is in this MultiSelect.

        To avoid confusion, only names are considered for comparison, not ID's.
        """

        for opt in self.multi_select:
            if opt.name == name:
                return True

        return False

    def __iter__(self):
        """Iterate over the SelectValue's in this property."""

        if self.multi_select is None:
            return None

        return iter(self.multi_select)

    @classmethod
    def __compose__(cls, *values):
        """Initialize a new MultiSelect from the given value(s)."""
        select = [SelectValue[value] for value in values if value is not None]

        return cls(multi_select=select)

    def append(self, *values):
        """Add selected values to this MultiSelect."""

        for value in values:
            if value is None:
                raise ValueError("'None' is an invalid value")

            if value not in self:
                self.multi_select.append(SelectValue[value])

    def remove(self, *values):
        """Remove selected values from this MultiSelect."""

        self.multi_select = [opt for opt in self.multi_select if opt.name not in values]

    @property
    def Values(self):
        """Return the names of each value in this MultiSelect as a list."""

        if self.multi_select is None:
            return None

        return [str(val) for val in self.multi_select if val.name is not None]


class People(PropertyValue):
    """Notion people type."""

    people: List[Person] = []
    type: Literal["people"] = "people"

    def __iter__(self):
        """Iterate over the User's in this property."""

        if self.people is None:
            return None

        return iter(self.people)

    def __contains__(self, other):
        """Determine if the given User or name is in this People.

        To avoid confusion, only names are considered for comparison (not ID's).
        """

        for user in self.people:
            if user == other:
                return True

            if user.name == other:
                return True

        return False

    def __len__(self):
        """Return the number of People in this property."""

        return len(self.people)

    def __getitem__(self, index):
        """Return the People object at the given index."""

        if self.people is None:
            raise IndexError("empty property")

        if index > len(self.people):
            raise IndexError("index out of range")

        return self.people[index]

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return ", ".join([str(user) for user in self.people])


class URL(PropertyValue, NativeTypeMixin):
    """Notion URL type."""

    url: Optional[str] = None
    type: Literal["url"] = "url"


class Email(PropertyValue, NativeTypeMixin):
    """Notion email type."""

    email: Optional[str] = None
    type: Literal["email"] = "email"


class PhoneNumber(PropertyValue, NativeTypeMixin):
    """Notion phone type."""

    phone_number: Optional[str] = None
    type: Literal["phone_number"] = "phone_number"


class Files(PropertyValue):
    """Notion files type."""

    files: List[Union[HostedFile, ExternalFile]] = []
    type: Literal["files"] = "files"

    def __contains__(self, other):
        """Determine if the given FileObject or name is in the property."""

        if self.files is None:
            return False

        for ref in self.files:
            if ref == other:
                return True

            if ref.name == other:
                return True

        return False

    def __str__(self) -> str:
        """Return a string representation of this property."""
        return "; ".join([str(file) for file in self.files])

    def __iter__(self):
        """Iterate over the FileObject's in this property."""

        if self.files is None:
            return None

        return iter(self.files)

    def __len__(self):
        """Return the number of Files in this property."""

        return len(self.files)

    def __getitem__(self, name):
        """Return the FileObject with the given name."""

        if self.files is None:
            return None

        for ref in self.files:
            if ref.name == name:
                return ref

        raise AttributeError("No such file")

    def __iadd__(self, obj):
        """Append the given `FileObject` in place."""

        if obj in self:
            raise ValueError(f"Item exists: {obj}")

        self.append(obj)
        return self

    def __isub__(self, obj):
        """Remove the given `FileObject` in place."""

        if obj not in self:
            raise ValueError(f"No such item: {obj}")

        self.remove(obj)
        return self

    def append(self, obj):
        """Append the given file reference to this property.

        :param ref: the `FileObject` to be added
        """
        self.files.append(obj)

    def remove(self, obj):
        """Remove the given file reference from this property.

        :param ref: the `FileObject` to be removed
        """
        self.files.remove(obj)


class FormulaResult(TypedObject, ABC):
    """A Notion formula result.

    This object contains the result of the expression in the database properties.
    """

    def __str__(self) -> str:
        """Return the formula result as a string."""
        return self.Result or ""

    @property
    def Result(self):
        """Return the result of this FormulaResult."""
        raise NotImplementedError("Result unavailable")


class StringFormula(FormulaResult):
    """A Notion string formula result."""

    string: Optional[str] = None
    type: Literal["string"] = "string"

    @property
    def Result(self):
        """Return the result of this StringFormula."""
        return self.string


class NumberFormula(FormulaResult):
    """A Notion number formula result."""

    number: Optional[Union[float, int]] = None
    type: Literal["number"] = "number"

    @property
    def Result(self):
        """Return the result of this NumberFormula."""
        return self.number


class DateFormula(FormulaResult):
    """A Notion date formula result."""

    date: Optional[DateRange] = None
    type: Literal["date"] = "date"

    @property
    def Result(self):
        """Return the result of this DateFormula."""
        return self.date


class BooleanFormula(FormulaResult):
    """A Notion boolean formula result."""

    boolean: Optional[bool] = None
    type: Literal["boolean"] = "boolean"

    @property
    def Result(self):
        """Return the result of this BooleanFormula."""
        return self.boolean


class Formula(PropertyValue):
    """A Notion formula property value."""

    formula: Optional[
        Union[StringFormula, NumberFormula, DateFormula, BooleanFormula]
    ] = None
    type: Literal["formula"] = "formula"

    def __str__(self) -> str:
        """Return the result of this formula as a string."""
        return str(self.Result or "")

    @property
    def Result(self):
        """Return the result of this Formula in its native type."""

        if self.formula is None:
            return None

        return self.formula.Result


class Relation(PropertyValue):
    """A Notion relation property value."""

    relation: List[ObjectReference] = []
    has_more: bool = False
    type: Literal["relation"] = "relation"

    @classmethod
    def __compose__(cls, *pages):
        """Return a `Relation` property with the specified pages."""
        return cls(relation=[ObjectReference[page] for page in pages])

    def __contains__(self, page):
        """Determine if the given page is in this Relation."""
        return ObjectReference[page] in self.relation

    def __iter__(self):
        """Iterate over the ObjectReference's in this property."""

        if self.relation is None:
            return None

        return iter(self.relation)

    def __len__(self):
        """Return the number of ObjectReference's in this property."""

        return len(self.relation)

    def __getitem__(self, index):
        """Return the ObjectReference object at the given index."""

        if self.relation is None:
            raise IndexError("empty property")

        if index > len(self.relation):
            raise IndexError("index out of range")

        return self.relation[index]

    def __iadd__(self, page):
        """Add the given page to this Relation in place."""

        ref = ObjectReference[page]

        if ref in self.relation:
            raise ValueError(f"Duplicate item: {ref.id}")

        self.relation.append(ref)

        return self

    def __isub__(self, page):
        """Remove the given page from this Relation in place."""

        ref = ObjectReference[page]

        if ref in self.relation:
            raise ValueError(f"No such item: {ref.id}")

        self.relation.remove(ref)

        return self


class RollupObject(TypedObject, ABC):
    """A Notion rollup property value."""

    function: Optional[Function] = None

    @property
    @abstractmethod
    def Value(self):
        """Return the native representation of this Rollup object."""


class RollupNumber(RollupObject):
    """A Notion rollup number property value."""

    number: Optional[Union[float, int]] = None
    type: Literal["number"] = "number"

    @property
    def Value(self):
        """Return the native representation of this Rollup object."""
        return self.number


class RollupDate(RollupObject):
    """A Notion rollup date property value."""

    date: Optional[DateRange] = None
    type: Literal["date"] = "date"

    @property
    def Value(self):
        """Return the native representation of this Rollup object."""
        return self.date


class RollupArray(RollupObject):
    """A Notion rollup array property value."""

    array: List[PropertyValue]
    type: Literal["array"] = "array"

    @property
    def Value(self):
        """Return the native representation of this Rollup object."""
        return self.array


class Rollup(PropertyValue):
    """A Notion rollup property value."""

    rollup: Optional[Union[RollupNumber, RollupDate, RollupArray]] = None
    type: Literal["rollup"] = "rollup"

    def __str__(self) -> str:
        """Return a string representation of this Rollup property."""

        if self.rollup is None:
            return ""

        value = self.rollup.Value
        if value is None:
            return ""

        return str(value)


class CreatedTime(PropertyValue, NativeTypeMixin):
    """A Notion created-time property value."""

    created_time: datetime
    type: Literal["created_time"] = "created_time"


class CreatedBy(PropertyValue):
    """A Notion created-by property value."""

    created_by: User
    type: Literal["created_by"] = "created_by"

    def __str__(self) -> str:
        """Return the contents of this property as a string."""
        return str(self.created_by)


class LastEditedTime(PropertyValue, NativeTypeMixin):
    """A Notion last-edited-time property value."""

    last_edited_time: datetime
    type: Literal["last_edited_time"] = "last_edited_time"


class LastEditedBy(PropertyValue):
    """A Notion last-edited-by property value."""

    last_edited_by: User
    type: Literal["last_edited_by"] = "last_edited_by"

    def __str__(self) -> str:
        """Return the contents of this property as a string."""
        return str(self.last_edited_by)


# https://developers.notion.com/reference/property-item-object
class PropertyItem(PropertyValue, DataObject):
    """A `PropertyItem` returned by the Notion API.

    Basic property items have a similar schema to corresponding property values.  As a
    result, these items share the `PropertyValue` type definitions.

    This class provides a placeholder for parsing property items, however objects
    parsed by this class will likely be `PropertyValue`'s instead.
    """

    object: Literal["property_item"] = "property_item"
