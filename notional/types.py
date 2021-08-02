"""Wrapper for Notion API data types."""
from abc import ABC, abstractmethod
from datetime import date, datetime


class NotionDataType(object):
    """Base class for Notion data types."""

    @classmethod
    def __init__(self, cls):
        """Initialize the object.

        :param cls: the type of data represented in this object
        """
        self.type = cls

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        raise NotImplementedError()


class PropertyValue(NotionDataType, ABC):
    """Base class for Notion properties."""

    @classmethod
    def __init__(self, cls, id):
        """Initialize the object.

        :param id: the short ID for the property, usually provided in the API response
        """
        super().__init__(cls)
        self.id = id

    @abstractmethod
    def to_json(self):
        """Serialize this value as a JSON object."""
        pass

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        raise NotImplementedError()

    @staticmethod
    def from_value(value):
        """Create a new instance of this property from the native value."""
        raise NotImplementedError()


class NativePropertyValue(PropertyValue):
    """Wrapper for classes that support native type assignments."""

    @classmethod
    def __init__(self, cls, id, value):
        """Initialize the object."""
        super().__init__(cls, id)
        self.value = value

    @classmethod
    def __repr__(self):
        """Return an explicit representation of this object."""
        return self.value

    @classmethod
    def __str__(self):
        """Return a string representation of this object."""
        return str(self.value)

    @classmethod
    def __eq__(self, other):
        """Determine if this property is equal to the given object.

        The objects are considered equal if the value wrapped in this property is
        equal to the provided value.
        """
        return self.value == other

    @classmethod
    def __ne__(self, other):
        """Determine if this property is not equal to the given object.

        The objects are considered unequal if the value wrapped in this property is
        unequal to the provided value.
        """
        return self.value != other

    @classmethod
    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return {"type": self.type, "id": self.id, self.type: self.value}


class Number(NativePropertyValue):
    """Simple number type."""

    @classmethod
    def __init__(self, id, value):
        """Initialize the object."""
        super().__init__("number", id, value)

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        return Number(id=data["id"], value=data["number"])

    @staticmethod
    def from_value(value):
        """Create a new Number from the native value."""
        return Number(id=None, value=value)


class Checkbox(NativePropertyValue):
    """Simple checkbox type; represented as a boolean."""

    @classmethod
    def __init__(self, id, value=False):
        """Initialize the object."""
        super().__init__("checkbox", id, value)

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        return Checkbox(id=data["id"], value=data["checkbox"])

    @staticmethod
    def from_value(value):
        """Create a new Checkbox from the native value."""
        return Checkbox(id=None, value=value)


class Date(PropertyValue):
    """Notion date type."""

    # TODO handle timestamps

    @classmethod
    def __init__(self, id, start, end):
        """Initialize the object."""
        super().__init__("date", id)
        self.start = start
        self.end = end

    @classmethod
    def __str__(self):
        """Return a string representation of this object."""
        return f"{self.start} :: {self.end}"

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        content = data["date"]

        if "start" not in content:
            raise ValueError('missing "start" in date object')

        start = content["start"]
        end = None

        if "end" in content:
            end = content["end"]

        return Date(id=data["id"], start=start, end=end)

    @staticmethod
    def from_value(value):
        """Create a new Date from the native value."""
        return Date(id=None, start=value)

    @classmethod
    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        start = self.start.isoformat()
        end = self.end.isoformat() if self.end else None

        return {
            "type": self.type,
            "id": self.id,
            "date": {"start": start, "end": end},
        }

    @staticmethod
    def parse_date_string(string):
        """Parse a date string into a simple date or date with timestamp."""
        if "T" in string or " " in string or ":" in string:
            return datetime.fromisoformat(string)

        return date.fromisoformat(string)


class RichText(PropertyValue):
    """Notion rich text type."""

    # TODO make elements into RichTextElement objects, rather than simple dict's

    @classmethod
    def __init__(self, id, text=list()):
        """Initialize the object."""
        super().__init__("rich_text", id)
        self.text = text

    @classmethod
    def __str__(self):
        """Return a string representation of this object."""
        return "".join(chunk["plain_text"] for chunk in self.text)

    @classmethod
    def __len__(self):
        """Return the number of elements in the RichText object."""
        return len(self.text)

    @classmethod
    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return {"type": self.type, "id": self.id, self.type: self.text}

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        return RichText(id=data["id"], text=data["rich_text"])

    @staticmethod
    def from_value(value):
        """Create a new RichText from the native string value."""
        text = [{"type": "text", "plain_text": value, "text": {"content": value}}]
        return RichText(id=None, text=text)


class Title(PropertyValue):
    """Notion title type."""

    # XXX wouldn't this make more sense as a simple string rather than rich text?
    # TODO make elements into RichTextElement objects, rather than simple dict's

    @classmethod
    def __init__(self, id, text=list()):
        """Initialize the object."""
        super().__init__("title", id)
        self.text = text

    @classmethod
    def __str__(self):
        """Return a string representation of this object."""
        return "".join(chunk["plain_text"] for chunk in self.text)

    @classmethod
    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return {"type": self.type, "id": self.id, self.type: self.text}

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        return Title(id=data["id"], text=data["title"])

    @staticmethod
    def from_value(value):
        """Create a new Title from the native value."""
        text = [{"type": "text", "plain_text": value, "text": {"content": value}}]
        return Title(id=None, text=text)


class SelectOne(PropertyValue):
    """Notion select type."""

    @classmethod
    def __init__(self, id, name, option_id, color=None):
        """Initialize the object."""
        super().__init__("select", id)

        if name is None and option_id is None:
            raise ValueError('must provide at least one of "name" or "option_id"')

        self.name = name
        self.option_id = option_id
        self.color = color

    @classmethod
    def __str__(self):
        """Return a string representation of this object."""
        return self.name or self.option_id or ""

    @staticmethod
    def from_json(data):
        """Deserialize this data from a JSON object."""
        content = data["select"]

        name = content["name"] if "name" in content else None
        option_id = content["id"] if "id" in content else None
        color = content["color"] if "color" in content else None

        return SelectOne(id=data["id"], name=name, option_id=option_id, color=color)

    @classmethod
    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        selected = {"id": self.option_id} if self.option_id else {"name": self.name}

        return {
            "type": self.type,
            "id": self.id,
            "select": selected,
        }

    @staticmethod
    def from_value(value):
        """Create a new SelectOne from the given string."""
        return SelectOne(id=None, name=value, option_id=None)


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
