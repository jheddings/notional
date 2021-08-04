"""Elements for working with rich text in Notion."""


class Annotations(object):
    """Style information for RichTextElement's."""

    # bold = Attribute("bold", False)
    # italic = Attribute("italic", False)

    def __init__(self):
        self.bold = False
        self.italic = False
        self.strikethrough = False
        self.underline = False
        self.code = False
        self.color = None

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
        if self.color is not None:
            return False
        return True

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
    """Base class for Notion rich text elements."""

    def __init__(self, type, text, style=None, href=None):
        self.type = type
        self.plain_text = text
        self.href = href
        self.annotations = style

    def __str__(self):
        """Return a string representation of this object."""
        return self.plain_text

    def to_json(self, **fields):
        """Convert this data type to JSON, suitable for sending to the API."""
        data = {"type": self.type, "plain_text": self.plain_text}

        if self.href:
            data["href"] = self.href

        if self.annotations:
            data["annotations"] = self.annotations.to_json()

        data.update(fields)

        return data

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

    def __init__(self, text, style=None, href=None):
        super().__init__("text", text, style, href)

    def to_json(self):
        data = super().to_json(text={"content": self.plain_text})

        if self.href is not None:
            data["link"] = {
                "type": url,
                "url": self.href,
            }

        return data
