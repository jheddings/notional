"""Base classes for working with the Notion API."""

import logging

from pydantic import BaseModel

log = logging.getLogger(__name__)


class DataObject(BaseModel):
    """The base for all API objects."""

    class Config:
        """pydantic model configuration"""

        underscore_attrs_are_private = False


class TypedObject(DataObject):
    """A type-referenced object.

    Many objects in the Notion API follow a generic->specific pattern with a 'type'
    parameter followed by additional data.  These objects must specify a `type`
    attribute to ensure that the correct object is created.
    """

    _subtypes_ = {}

    type: str

    # following the method found in these examples:
    # - https://github.com/samuelcolvin/pydantic/discussions/3091

    def __init_subclass__(cls, type=None, **kwargs):
        """Register the subtype by name for faster lookup."""
        super().__init_subclass__(**kwargs)

        if type is not None:
            sub_type = type

        elif hasattr(cls, "__type__"):
            sub_type = getattr(cls, "__type__")

        else:
            sub_type = cls.__name__

        # if sub_type in cls._subtypes_:
        #    raise ValueError(f"Duplicate subtype: {sub_type} {cls}")

        log.debug("registered new subtype: %s => %s", sub_type, cls)

        cls._subtypes_[sub_type] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        """Instantiate the correct object based on the 'type' field."""

        data_type = data.get("type")

        if data_type is None:
            raise ValueError("Missing 'type' in TypedObject")

        sub = cls._subtypes_.get(data_type)

        if sub is None:
            raise TypeError(f"Unsupport sub-type: {data_type}")

        log.debug("converting type %s :: %s => %s", data_type, cls, sub)

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

    pass
