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

    type: str

    # using method found on pydantic feature request (#619)
    # https://github.com/samuelcolvin/pydantic/issues/619#issuecomment-713508861

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        data_type = data.get("type")

        if data_type is None:
            raise ValueError("Missing 'type' in TypedObject")

        for sub in cls.__subclasses__():
            if hasattr(sub, "type"):
                sub_type = getattr(sub, "type")
            elif hasattr(sub, "__type__"):
                sub_type = getattr(sub, "__type__")
            elif hasattr(sub, "__fields__"):
                sub_type = sub.__fields__["type"].default
            else:
                raise TypeError("Unable to find 'type' identifier in class")

            if data_type == sub_type:
                log.debug("converting type %s :: %s => %s", data_type, cls, sub)
                return sub(**data)

        raise TypeError(f"Unsupport sub-type: {data_type}")


class NestedObject(DataObject):
    """Represents an API object with nested data.

    These objects require a 'type' property in the outer data and a matching property
    of the same name in the inner data.

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

    pass
