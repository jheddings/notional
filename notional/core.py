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
    parameter followed by additional data.  These objects require a `__type__` attribute
    to ensure that the correct object is created.
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
            if data_type == sub.__type__:
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
