"""Objects representing a database schema."""

from typing import Any, Dict, List

from .core import DataObject, NestedObject, TypedObject


class PropertyObject(TypedObject):
    """Base class for Notion property objects."""

    id: str
    name: str


Schema = Dict[str, PropertyObject]
"""A database schema, mapping property names to object configurations."""


class TitleProperty(PropertyObject, type="title"):
    """Defines the title configuration for a database property."""

    title: Any = None


class RichTextProperty(PropertyObject, type="rich_text"):
    """Defines the rich text configuration for a database property."""

    rich_text: Any = None


class NumberProperty(PropertyObject, type="number"):
    """Defines the number configuration for a database property."""

    class NestedNumber(NestedObject):
        format: str = "number"

    number: NestedNumber = None


class SelectOption(DataObject):
    """Options for select & multi-select objects."""

    name: str
    id: str = None
    color: str = None


class SelectProperty(PropertyObject, type="select"):
    """Defines the select configuration for a database property."""

    class NestedSelect(NestedObject):
        options: List[SelectOption] = []

    select: NestedSelect = None


class MultiSelectProperty(PropertyObject, type="multi_select"):
    """Defines the multi-select configuration for a database property."""

    class NestedSelect(NestedObject):
        options: List[SelectOption] = []

    multi_select: NestedSelect = None


class DateProperty(PropertyObject, type="date"):
    """Defines the date configuration for a database property."""

    date: Any = None


class PeopleProperty(PropertyObject, type="people"):
    """Defines the people configuration for a database property."""

    people: Any = None


class FilesProperty(PropertyObject, type="files"):
    """Defines the files configuration for a database property."""

    files: Any = None


class CheckboxProperty(PropertyObject, type="checkbox"):
    """Defines the checkbox configuration for a database property."""

    checkbox: Any = None


class EmailProperty(PropertyObject, type="email"):
    """Defines the email configuration for a database property."""

    email: Any = None


class UrlProperty(PropertyObject, type="url"):
    """Defines the URL configuration for a database property."""

    url: Any = None


class PhoneNumber(PropertyObject, type="phone_number"):
    """Defines the phone number configuration for a database property."""

    phone_number: Any = None


class FormulaProperty(PropertyObject, type="formula"):
    """Defines the formula configuration for a database property."""

    class NestedFormula(NestedObject):
        expression: str

    formula: NestedFormula = None


class RelationProperty(PropertyObject, type="relation"):
    """Defines the relation configuration for a database property."""

    class NestedRelation(NestedObject):
        database_id: str
        synced_property_name: str = None
        synced_property_id: str = None

    relation: NestedRelation = None


class RollupProperty(PropertyObject, type="rollup"):
    """Defines the rollup configuration for a database property."""

    class NestedRollup(NestedObject):
        relation_property_name: str
        relation_property_id: str
        rollup_property_name: str
        rollup_property_id: str
        function: str

    rollup: NestedRollup = None


class CreatedTimeProperty(PropertyObject, type="created_time"):
    """Defines the created-time configuration for a database property."""

    created_time: Any = None


class CreatedByProperty(PropertyObject, type="created_by"):
    """Defines the created-by configuration for a database property."""

    created_by: Any = None


class LastEditedByProperty(PropertyObject, type="last_edited_by"):
    """Defines the last-edited-by configuration for a database property."""

    last_edited_by: Any = None


class LastEditedTimeProperty(PropertyObject, type="last_edited_time"):
    """Defines the last-edited-time configuration for a database property."""

    last_edited_time: Any = None
