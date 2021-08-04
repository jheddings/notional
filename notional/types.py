"""Wrapper for Notion API data types."""
from abc import ABC, abstractmethod
from datetime import date, datetime

from .text import RichTextElement


class NotionDataType(object):
    """Base class for Notion data types."""

    def __init__(self, cls):
        self.type = cls

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        raise NotImplementedError()


class PropertyValue(NotionDataType, ABC):
    """Base class for Notion properties."""

    def __init__(self, cls, id):
        super().__init__(cls)
        self.id = id

    @abstractmethod
    def to_json(self, **fields):
        """Serialize this value as a JSON object."""
        data = {"type": self.type}

        if self.id is not None:
            data["id"] = self.id

        data.update(fields)

        return data

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        raise NotImplementedError()

    @classmethod
    def from_value(cls, value):
        """Create a new instance of this property from the native value."""
        raise NotImplementedError()


class NativePropertyValue(PropertyValue):
    """Wrapper for classes that support native type assignments."""

    def __init__(self, cls, id, value):
        super().__init__(cls, id)
        self.value = value

    def __repr__(self):
        """Return an explicit representation of this object."""
        return self.value

    def __str__(self):
        """Return a string representation of this object."""
        return str(self.value)

    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        The objects are considered equal if the value wrapped in this property is
        equal to the provided value.
        """
        return self.value == other

    def __ne__(self, other):
        """Determine if this property is not equal to the given object.

        The objects are considered unequal if the value wrapped in this property is
        unequal to the provided value.
        """
        return self.value != other

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return super().to_json(**{self.type: self.value})

    @classmethod
    def from_value(cls, value):
        """Create a new value from the native value."""
        return cls(id=None, value=value)


class Number(NativePropertyValue):
    """Simple number type."""

    def __init__(self, id, value=None):
        super().__init__("number", id, value)

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        return cls(id=data["id"], value=data["number"])


class Checkbox(NativePropertyValue):
    """Simple checkbox type; represented as a boolean."""

    def __init__(self, id, value=False):
        super().__init__("checkbox", id, value)

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        return cls(id=data["id"], value=data["checkbox"])


class Date(PropertyValue):
    """Notion complex date type - may include timestamp and/or be a date range."""

    def __init__(self, id, start, end=None):
        super().__init__("date", id)
        self.start = start
        self.end = end

    def __str__(self):
        """Return a string representation of this object."""
        return f"{self.start} :: {self.end}"

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        content = data["date"]

        if "start" not in content:
            raise ValueError('missing "start" in date object')

        start = content["start"]
        end = None

        if "end" in content:
            end = content["end"]

        return cls(id=data["id"], start=start, end=end)

    @classmethod
    def from_value(cls, value):
        """Create a new Date from the native value."""
        return cls(id=None, start=value)

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return super().to_json(
            date={
                "start": self.start.isoformat(),
                "end": self.end.isoformat() if self.end else None,
            }
        )

    @staticmethod
    def parse_date_string(string):
        """Parse a date string into a simple date or date with timestamp."""
        if "T" in string or " " in string or ":" in string:
            return datetime.fromisoformat(string)

        return date.fromisoformat(string)


class Text(PropertyValue):
    """Standard Notion text properties."""

    def __init__(self, type, id, text=list()):
        super().__init__(type, id)
        self.text = text

    def __str__(self):
        """Return a string representation of this object."""
        return "".join(str(elem) for elem in self.text)

    def __len__(self):
        """Return the number of elements in the RichText object."""
        return len(self.text)

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        rtf = [elem.to_json() for elem in self.text]
        return super().to_json(**{self.type: rtf})

    @classmethod
    def from_value(cls, value):
        """Create a new RichText from the native string value."""
        rtf = TextElement(text=value)
        return cls(id=None, text=[rtf])


class RichText(Text):
    """Notion rich text type."""

    def __init__(self, id, text=list()):
        super().__init__(type="rich_text", id=id, text=text)

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        rtf = [RichTextElement.from_json(elem) for elem in data["rich_text"]]
        return cls(id=data["id"], text=rtf)


class Title(Text):
    """Notion title type."""

    def __init__(self, id, text=list()):
        super().__init__(type="title", id=id, text=text)

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        rtf = [RichTextElement.from_json(elem) for elem in data["title"]]
        return cls(id=data["id"], text=rtf)


class SelectOne(PropertyValue):
    """Notion select type."""

    def __init__(self, id, name, option_id, color=None):
        super().__init__("select", id)

        if name is None and option_id is None:
            raise ValueError('must provide at least one of "name" or "option_id"')

        self.name = name
        self.option_id = option_id
        self.color = color

    def __str__(self):
        """Return a string representation of this object."""
        return self.name or self.option_id or ""

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return super().to_json(
            select={"id": self.option_id} if self.option_id else {"name": self.name}
        )

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        content = data["select"]

        name = content["name"] if "name" in content else None
        option_id = content["id"] if "id" in content else None
        color = content["color"] if "color" in content else None

        return cls(id=data["id"], name=name, option_id=option_id, color=color)

    @classmethod
    def from_value(cls, value):
        """Create a new SelectOne from the given string."""
        return cls(id=None, name=value, option_id=None)


property_type_map = {
    "title": Title,
    "number": Number,
    "date": Date,
    "checkbox": Checkbox,
    "select": SelectOne,
    "rich_text": RichText,
}


def notion_to_python(data):
    """Convert the raw data from Notion to a python object."""
    if data is None:
        return None

    if "type" not in data:
        raise ValueError("unable to determine content type")

    cls = property_type_map.get(data["type"], None)

    if cls is None:
        raise TypeError(f'unsupported data type: {data["type"]}')

    return cls.from_json(data)


def python_to_notion(value, cls):
    """Convert the python object to Notion API data.

    This will raise a TypeError if a conversion is not found.
    """
    if isinstance(value, cls):
        return value.to_json()

    try:
        obj = cls.from_value(value)
    except NotImplementedError:
        raise TypeError(f"Unsupported data type - {cls}")

    return obj.to_json()
