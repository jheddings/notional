"""Elements for working with rich text in Notion."""


class Annotations(object):
    """Style information for a RichTextElement."""

    def __init__(self):
        self.bold = False
        self.italic = False
        self.strikethrough = False
        self.underline = False
        self.code = False
        self.color = None

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return {
            "bold": self.bold,
            "italic": self.italic,
            "strikethrough": self.strikethrough,
            "underline": self.underline,
            "code": self.code,
            "color": self.color,
        }

    @property
    def is_plain(self):
        if self.bold:
            return False
        if self.italic:
            return False
        if self.strikethrough:
            return False
        if self.underline:
            return False
        if self.code:
            return False
        if self.color:
            return False
        return True

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        style = cls()

        if "bold" in data:
            style.bold = data["bold"]

        if "italic" in data:
            style.italic = data["italic"]

        if "strikethrough" in data:
            style.strikethrough = data["strikethrough"]

        if "underline" in data:
            style.underline = data["underline"]

        if "code" in data:
            style.code = data["code"]

        if "color" in data:
            style.color = data["color"]

        return style


class RichTextElement(object):
    """Notion rich text element."""

    def __init__(self, type, text, style=None, href=None):
        self.type = type
        self.plain_text = text
        self.href = href
        self.annotations = style

    def __str__(self):
        """Return a string representation of this object."""
        return self.plain_text

    def to_json(self):
        """Convert this data type to JSON, suitable for sending to the API."""
        return {"type": self.type, "id": self.id, self.type: self.text}

    @classmethod
    def from_json(cls, data):
        """Deserialize this data from a JSON object."""
        style = None

        if "annotations" in data:
            style = Annotations.from_json(data["annotations"])

        return cls(
            type=data["type"],
            text=data["plain_text"],
            href=data["href"] if "href" in data else None,
            style=style,
        )


class TextElement(RichTextElement):
    """Notion text element."""

    def __init__(self, text):
        self.type = type
