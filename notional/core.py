"""Base classes for working with the Notion API."""

import inspect
import json
import logging
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, validator
from pydantic.main import validate_model

log = logging.getLogger(__name__)


def make_api_safe(data):
    """Recursively convert the given data to an API-safe form.

    This is mostly to handle data types that will not directly serialize to JSON.
    """

    if isinstance(data, date) or isinstance(data, datetime):
        return data.isoformat()

    elif isinstance(data, UUID):
        return data.hex

    elif isinstance(data, Enum):
        return data.value

    elif isinstance(data, dict):
        return {name: make_api_safe(value) for name, value in data.items()}

    elif isinstance(data, list):
        return [make_api_safe(value) for value in data]

    elif isinstance(data, tuple):
        return [make_api_safe(value) for value in data]

    return data


class DataObject(BaseModel):
    """The base for all API objects."""

    # See https://github.com/samuelcolvin/pydantic/issues/1577
    def __setattr__(self, name, value):
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            setters = inspect.getmembers(
                self.__class__,
                predicate=lambda x: isinstance(x, property) and x.fset is not None,
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise e

    def refresh(__pydantic_self__, **data):
        """Refresh the internal attributes with new data."""

        values, fields, error = validate_model(__pydantic_self__.__class__, data)

        if error:
            raise error

        log.debug("refreshing object values -- %s", values)

        object.__setattr__(__pydantic_self__, "__dict__", values)

        return __pydantic_self__

    def to_api(self):
        """Convert to a suitable representation for the Notion API."""

        # the API doesn't like "undefined" values...

        data = self.dict(exclude_none=True)

        # we need to convert "special" types to string forms to help the JSON encoder.
        # there are efforts underway in pydantic to make this easier, but for now...

        # XXX this method has promise, but converts the entire value to a single string
        # return {name: json.dumps(value, default=str) for name, value in data.items()}

        return make_api_safe(data)


class NamedObject(DataObject):
    """A Notion API object."""

    object: str = None

    def __init_subclass__(cls, object=None, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.object = object


class TypedObject(DataObject):
    """A type-referenced object.

    Many objects in the Notion API follow a generic->specific pattern with a 'type'
    parameter followed by additional data.  These objects must specify a `type`
    attribute to ensure that the correct object is created.
    """

    type: str = None

    # modified from the methods described in this discussion:
    # - https://github.com/samuelcolvin/pydantic/discussions/3091

    def __init_subclass__(cls, type=None, **kwargs):
        """Register the subtypes of the TypedObject subclass."""
        super().__init_subclass__(**kwargs)

        if type is not None:
            sub_type = type

            # also set the default for the class 'type' field
            cls.type = sub_type

        elif hasattr(cls, "__type__"):
            sub_type = getattr(cls, "__type__")

        else:
            sub_type = cls.__name__

        # initialize a _subtypes_ map for each direct child of TypedObject

        # this allows different class trees to have the same 'type' name
        # but point to a different object (e.g. the 'date' type may have
        # different implementations depending where it is used in the API)

        # also, due to the order in which typed classes are defined, once
        # the map is defined for a subclass of TypedObject, any further
        # descendants of that class will have the new map via inheritance

        if TypedObject in cls.__bases__ and not hasattr(cls, "_subtypes_"):
            cls._subtypes_ = dict()

        if sub_type in cls._subtypes_:
            raise ValueError(f"Duplicate subtype for class - {sub_type} :: {cls}")

        log.debug("registered new subtype: %s => %s", sub_type, cls)

        cls._subtypes_[sub_type] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def parse_obj(cls, obj):
        return cls._convert_to_real_type_(obj)

    @classmethod
    def _convert_to_real_type_(cls, data):
        """Instantiate the correct object based on the 'type' field."""

        if isinstance(data, cls):
            return data

        if not isinstance(data, dict):
            raise ValueError("Invalid 'data' object")

        data_type = data.get("type")

        if data_type is None:
            raise ValueError("Missing 'type' in TypedObject")

        if not hasattr(cls, "_subtypes_"):
            raise TypeError(f"Invalid TypedObject: {cls} - missing _subtypes_")

        sub = cls._subtypes_.get(data_type)

        if sub is None:
            raise TypeError(f"Unsupport sub-type: {data_type}")

        log.debug(
            "initializing typed object %s :: %s => %s -- %s", cls, data_type, sub, data
        )

        return sub(**data)


class NestedObject(DataObject):
    """Represents an API object with nested data.

    These objects require a 'type' property and a matching property of the same
    name, which holds additional data.

    For example, this contains a nested 'text' object:

        data = {
            type: "text",
            ...
            text: {
                ...
            }
        }

    Currently, this is a convenience class for clarity - it does not provide additional
    functionality at this time.
    """

    # XXX can we somehow help provide pass-through access from the outer class?

    # some ideas...
    #   use __call__ of the outer class to access inner metadata object
    #   use __getitem__ of the outer class to access inner metadata properties
