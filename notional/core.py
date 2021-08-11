"""Base classes for working with the Notion API."""

import dataclasses
import logging
from dataclasses import dataclass, is_dataclass

log = logging.getLogger(__name__)


class DataObject(object):
    """The base for all API objects."""

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the Notion API."""
        if is_dataclass(self):
            return dataclasses.asdict(self)

        raise TypeError("unable to convert object to JSON")

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object, typically from the Notion API."""
        print(data)
        if is_dataclass(cls):
            return cls._expand_dataclass(data)

        raise TypeError("unable to convert JSON to object")

    @classmethod
    def _expand_dataclass(cls, data):
        """Convert data in dict to more complex data classes."""

        # replace simple types with complex types where posssible...
        for field in dataclasses.fields(cls):
            log.debug("expanding %s => %s", field.name, field.type)

            # TODO find a way to handle List and Dict types automatically...

            convert = getattr(field.type, "from_json", None)
            if convert is not None and callable(convert):
                raw = data.get(field.name)
                rich = convert(raw)
                data[field.name] = rich

                log.debug("converted %s => %s", field.type, rich)

        return cls(**data)


@dataclass
class TypedObject(DataObject):
    @classmethod
    def from_json(cls, data):
        """Override the default method to provide a factory for subclass types."""

        # prevent infinite loops from subclasses...
        if issubclass(cls, TypedObject):
            data_type = data.get("type")

            for sub in cls.__subclasses__():
                if data_type == sub.__type__:
                    return sub.from_json(data)

        return super().from_json(data)


@dataclass
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
