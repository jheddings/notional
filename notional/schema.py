"""Objects representing a database schema."""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from .core import DataObject, NestedObject, TypedObject


class Function(str, Enum):
    """Standard aggregation functions."""

    count_all = "count_all"
    count_values = "count_values"
    count_unique_values = "count_unique_values"
    count_empty = "count_empty"
    count_not_empty = "count_not_empty"

    percent_empty = "percent_empty"
    percent_not_empty = "percent_not_empty"

    average = "average"
    min = "min"
    max = "max"
    median = "median"
    range = "range"
    sum = "sum"

    earliest_date = "earliest_date"
    latest_date = "latest_date"

    show_original = "show_original"


class PropertyObject(TypedObject):
    """Base class for Notion property objects."""

    id: Optional[str] = None
    name: Optional[str] = None


class Title(PropertyObject, type="title"):
    """Defines the title configuration for a database property."""

    title: Any = {}


class RichText(PropertyObject, type="rich_text"):
    """Defines the rich text configuration for a database property."""

    rich_text: Any = {}


class Number(PropertyObject, type="number"):
    """Defines the number configuration for a database property."""

    class NestedData(NestedObject):
        format: str = "number"

    number: NestedData = {}

    @classmethod
    def format(cls, format):
        return cls(number=cls.NestedData(format=format))


class SelectOption(DataObject):
    """Options for select & multi-select objects."""

    name: str
    id: str = None
    color: str = None


class Select(PropertyObject, type="select"):
    """Defines the select configuration for a database property."""

    class NestedData(NestedObject):
        options: List[SelectOption] = []

    select: NestedData = None

    @classmethod
    def options(cls, *options):
        return cls(select=cls.NestedData(options=options))


class MultiSelect(PropertyObject, type="multi_select"):
    """Defines the multi-select configuration for a database property."""

    class NestedData(NestedObject):
        options: List[SelectOption] = []

    multi_select: NestedData = None


class Date(PropertyObject, type="date"):
    """Defines the date configuration for a database property."""

    date: Any = {}


class People(PropertyObject, type="people"):
    """Defines the people configuration for a database property."""

    people: Any = {}


class Files(PropertyObject, type="files"):
    """Defines the files configuration for a database property."""

    files: Any = {}


class Checkbox(PropertyObject, type="checkbox"):
    """Defines the checkbox configuration for a database property."""

    checkbox: Any = {}


class Email(PropertyObject, type="email"):
    """Defines the email configuration for a database property."""

    email: Any = {}


class URL(PropertyObject, type="url"):
    """Defines the URL configuration for a database property."""

    url: Any = {}


class PhoneNumber(PropertyObject, type="phone_number"):
    """Defines the phone number configuration for a database property."""

    phone_number: Any = {}


class Formula(PropertyObject, type="formula"):
    """Defines the formula configuration for a database property."""

    class NestedData(NestedObject):
        expression: str

    formula: NestedData = None


class Relation(PropertyObject, type="relation"):
    """Defines the relation configuration for a database property."""

    class NestedData(NestedObject):
        database_id: UUID
        synced_property_name: str = None
        synced_property_id: str = None

    relation: NestedData = None


class Rollup(PropertyObject, type="rollup"):
    """Defines the rollup configuration for a database property."""

    class NestedData(NestedObject):
        relation_property_name: str
        relation_property_id: str
        rollup_property_name: str
        rollup_property_id: str
        function: Function

    rollup: NestedData


class CreatedTime(PropertyObject, type="created_time"):
    """Defines the created-time configuration for a database property."""

    created_time: Any = {}


class CreatedBy(PropertyObject, type="created_by"):
    """Defines the created-by configuration for a database property."""

    created_by: Any = {}


class LastEditedBy(PropertyObject, type="last_edited_by"):
    """Defines the last-edited-by configuration for a database property."""

    last_edited_by: Any = {}


class LastEditedTime(PropertyObject, type="last_edited_time"):
    """Defines the last-edited-time configuration for a database property."""

    last_edited_time: Any = {}
