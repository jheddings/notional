"""Objects representing a database schema."""

from enum import Enum
from typing import Any, List, Literal, Optional, Union
from uuid import UUID

from pydantic import field_validator

from .core import NotionObject, TypedObject
from .text import Color


class Function(str, Enum):
    """Standard aggregation functions."""

    COUNT = "count"
    COUNT_VALUES = "count_values"
    COUNT_PER_GROUP = "count_per_group"

    EMPTY = "empty"
    NOT_EMPTY = "not_empty"

    CHECKED = "checked"
    UNCHECKED = "unchecked"

    PERCENT_EMPTY = "percent_empty"
    PERCENT_NOT_EMPTY = "percent_not_empty"
    PERCENT_CHECKED = "percent_checked"
    PERCENT_PER_GROUP = "percent_per_group"

    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    RANGE = "range"
    SUM = "sum"

    DATE_RANGE = "date_range"
    EARLIEST_DATE = "earliest_date"
    LATEST_DATE = "latest_date"

    SHOW_ORIGINAL = "show_original"
    SHOW_UNIQUE = "show_unique"
    UNIQUE = "unique"


class NumberFormat(str, Enum):
    """Available number formats in Notion."""

    NUMBER = "number"
    NUMBER_WITH_COMMAS = "number_with_commas"
    PERCENT = "percent"
    DOLLAR = "dollar"
    CANADIAN_DOLLAR = "canadian_dollar"
    EURO = "euro"
    POUND = "pound"
    YEN = "yen"
    RUBLE = "ruble"
    RUPEE = "rupee"
    WON = "won"
    YUAN = "yuan"
    REAL = "real"
    LIRA = "lira"
    RUPIAH = "rupiah"
    FRANC = "franc"
    HONG_KONG_DOLLAR = "hong_kong_dollar"
    NEW_ZEALAND_DOLLAR = "new_zealand_dollar"
    KRONA = "krona"
    NORWEGIAN_KRONE = "norwegian_krone"
    MEXICAN_PESO = "mexican_peso"
    RAND = "rand"
    NEW_TAIWAN_DOLLAR = "new_taiwan_dollar"
    DANISH_KRONE = "danish_krone"
    ZLOTY = "zloty"
    BAHT = "baht"
    FORINT = "forint"
    KORUNA = "koruna"
    SHEKEL = "shekel"
    CHILEAN_PESO = "chilean_peso"
    PHILIPPINE_PESO = "philippine_peso"
    DIRHAM = "dirham"
    COLOMBIAN_PESO = "colombian_peso"
    RIYAL = "riyal"
    RINGGIT = "ringgit"
    LEU = "leu"
    ARGENTINE_PESO = "argentine_peso"
    URUGUAYAN_PESO = "uruguayan_peso"


class PropertyObject(TypedObject):
    """Base class for Notion property objects."""

    id: Optional[str] = None
    name: Optional[str] = None


class Title(PropertyObject):
    """Defines the title configuration for a database property."""

    title: Any = {}
    type: Literal["title"] = "title"


class RichText(PropertyObject):
    """Defines the rich text configuration for a database property."""

    rich_text: Any = {}
    type: Literal["rich_text"] = "rich_text"


class Number(PropertyObject):
    """Defines the number configuration for a database property."""

    class _NestedData(NotionObject):
        format: NumberFormat = NumberFormat.NUMBER

        # leads to better error messages; see https://github.com/pydantic/pydantic/issues/355
        @field_validator("format", mode="before")
        def validate_enum_field(cls, field: str):
            return NumberFormat(field)

    number: _NestedData
    type: Literal["number"] = "number"

    @classmethod
    def __compose__(cls, format):
        """Create a `Number` object with the expected format."""
        return cls(number=cls._NestedData(format=format))


class SelectOption(NotionObject):
    """Options for select & multi-select objects."""

    name: str
    id: Optional[str] = None
    color: str = Color.DEFAULT

    @classmethod
    def __compose__(cls, name, color=Color.DEFAULT):
        """Create a `SelectOption` object from the given name and color."""
        return cls(name=name, color=color)


class Select(PropertyObject):
    """Defines the select configuration for a database property."""

    class _NestedData(NotionObject):
        options: List[SelectOption] = []

    select: _NestedData
    type: Literal["select"] = "select"

    @classmethod
    def __compose__(cls, options):
        """Create a `Select` object from the list of `SelectOption`'s."""
        return cls(select=cls._NestedData(options=options))


class MultiSelect(PropertyObject):
    """Defines the multi-select configuration for a database property."""

    class _NestedData(NotionObject):
        options: List[SelectOption] = []

    multi_select: _NestedData
    type: Literal["multi_select"] = "multi_select"


class Status(PropertyObject):
    """Defines the status configuration for a database property."""

    status: Any = {}
    type: Literal["status"] = "status"


class Date(PropertyObject):
    """Defines the date configuration for a database property."""

    date: Any = {}
    type: Literal["date"] = "date"


class People(PropertyObject):
    """Defines the people configuration for a database property."""

    people: Any = {}
    type: Literal["people"] = "people"


class Files(PropertyObject):
    """Defines the files configuration for a database property."""

    files: Any = {}
    type: Literal["files"] = "files"


class Checkbox(PropertyObject):
    """Defines the checkbox configuration for a database property."""

    checkbox: Any = {}
    type: Literal["checkbox"] = "checkbox"


class Email(PropertyObject):
    """Defines the email configuration for a database property."""

    email: Any = {}
    type: Literal["email"] = "email"


class URL(PropertyObject):
    """Defines the URL configuration for a database property."""

    url: Any = {}
    type: Literal["url"] = "url"


class PhoneNumber(PropertyObject):
    """Defines the phone number configuration for a database property."""

    phone_number: Any = {}
    type: Literal["phone_number"] = "phone_number"


class Formula(PropertyObject):
    """Defines the formula configuration for a database property."""

    class _NestedData(NotionObject):
        expression: str

    formula: _NestedData
    type: Literal["formula"] = "formula"


class PropertyRelation(TypedObject):
    """Defines common configuration for a property relation."""

    database_id: UUID


class SinglePropertyRelation(PropertyRelation):
    """Defines a single-property relation configuration for a database property."""

    single_property: Any = {}
    type: Literal["single_property"] = "single_property"

    @classmethod
    def __compose__(cls, dbref: Union[str, UUID]):
        """Create a `single_property` relation using the target database reference."""
        return Relation(relation=SinglePropertyRelation(database_id=dbref))


class DualPropertyRelation(PropertyRelation):
    """Defines a dual-property relation configuration for a database property."""

    class _NestedData(NotionObject):
        synced_property_name: Optional[str] = None
        synced_property_id: Optional[str] = None

    dual_property: _NestedData
    type: Literal["dual_property"] = "dual_property"


class Relation(PropertyObject):
    """Defines the relation configuration for a database property."""

    relation: Union[SinglePropertyRelation, DualPropertyRelation]
    type: Literal["relation"] = "relation"


class Rollup(PropertyObject):
    """Defines the rollup configuration for a database property."""

    class _NestedData(NotionObject):
        function: Function = Function.COUNT

        relation_property_name: Optional[str] = None
        relation_property_id: Optional[str] = None

        rollup_property_name: Optional[str] = None
        rollup_property_id: Optional[str] = None

        # leads to better error messages; see https://github.com/pydantic/pydantic/issues/355
        @field_validator("function", mode="before")
        def validate_enum_field(cls, field: str):
            return Function(field)

    rollup: _NestedData
    type: Literal["rollup"] = "rollup"


class CreatedTime(PropertyObject):
    """Defines the created-time configuration for a database property."""

    created_time: Any = {}
    type: Literal["created_time"] = "created_time"


class CreatedBy(PropertyObject):
    """Defines the created-by configuration for a database property."""

    created_by: Any = {}
    type: Literal["created_by"] = "created_by"


class LastEditedBy(PropertyObject):
    """Defines the last-edited-by configuration for a database property."""

    last_edited_by: Any = {}
    type: Literal["last_edited_by"] = "last_edited_by"


class LastEditedTime(PropertyObject):
    """Defines the last-edited-time configuration for a database property."""

    last_edited_time: Any = {}
    type: Literal["last_edited_time"] = "last_edited_time"
