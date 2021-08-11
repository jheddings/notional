"""Objects representing a database schema."""

from typing import Any, Dict, List

from .core import DataObject, NestedObject, TypedObject


class PropertyObject(TypedObject):
    """Base class for Notion property objects."""

    id: str
    name: str


Schema = Dict[str, PropertyObject]
"""A database schema, mapping property names to object configurations."""


class TitleProperty(PropertyObject):
    """Defines the title configuration for a database property."""

    __type__ = "title"

    title: Any = None


class RichTextProperty(PropertyObject):
    """Defines the rich text configuration for a database property."""

    __type__ = "rich_text"

    rich_text: Any = None


class NumberProperty(PropertyObject):
    """Defines the number configuration for a database property."""

    __type__ = "number"

    class NestedNumber(NestedObject):
        format: str = "number"

    number: NestedNumber = None


class SelectOption(DataObject):
    """Options for select & multi-select objects."""

    name: str
    id: str = None
    color: str = None


class SelectProperty(PropertyObject):
    """Defines the select configuration for a database property."""

    __type__ = "select"

    class NestedSelect(NestedObject):
        options: List[SelectOption] = []

    select: NestedSelect = None


class MultiSelectProperty(PropertyObject):
    """Defines the multi-select configuration for a database property."""

    __type__ = "multi_select"

    class NestedSelect(NestedObject):
        options: List[SelectOption] = []

    multi_select: NestedSelect = None


class DateProperty(PropertyObject):
    """Defines the date configuration for a database property."""

    __type__ = "date"

    date: Any = None


class PeopleProperty(PropertyObject):
    """Defines the people configuration for a database property."""

    __type__ = "people"

    people: Any = None


class FilesProperty(PropertyObject):
    """Defines the files configuration for a database property."""

    __type__ = "files"

    files: Any = None


class CheckboxProperty(PropertyObject):
    """Defines the checkbox configuration for a database property."""

    __type__ = "checkbox"

    checkbox: Any = None


class EmailProperty(PropertyObject):
    """Defines the email configuration for a database property."""

    __type__ = "email"

    email: Any = None


class UrlProperty(PropertyObject):
    """Defines the URL configuration for a database property."""

    __type__ = "url"

    url: Any = None


class PhoneNumber(PropertyObject):
    """Defines the phone number configuration for a database property."""

    __type__ = "phone_number"

    phone_number: Any = None


class FormulaProperty(PropertyObject):
    """Defines the formula configuration for a database property."""

    __type__ = "formula"

    class NestedFormula(NestedObject):
        expression: str

    formula: NestedFormula = None


class RelationProperty(PropertyObject):
    """Defines the relation configuration for a database property."""

    __type__ = "relation"

    class NestedRelation(NestedObject):
        database_id: str
        synced_property_name: str = None
        synced_property_id: str = None

    relation: NestedRelation = None


class RollupProperty(PropertyObject):
    """Defines the rollup configuration for a database property."""

    __type__ = "rollup"

    class NestedRollup(NestedObject):
        relation_property_name: str
        relation_property_id: str
        rollup_property_name: str
        rollup_property_id: str
        function: str

    rollup: NestedRollup = None


class CreatedTimeProperty(PropertyObject):
    """Defines the created-time configuration for a database property."""

    __type__ = "created_time"

    created_time: Any = None


class CreatedByProperty(PropertyObject):
    """Defines the created-by configuration for a database property."""

    __type__ = "created_by"

    created_by: Any = None


class LastEditedByProperty(PropertyObject):
    """Defines the last-edited-by configuration for a database property."""

    __type__ = "last_edited_by"

    last_edited_by: Any = None


class LastEditedTimeProperty(PropertyObject):
    """Defines the last-edited-time configuration for a database property."""

    __type__ = "last_edited_time"

    last_edited_time: Any = None
