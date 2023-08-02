"""Wrapper for Notion user objects."""

from enum import Enum
from typing import Literal, Optional
from uuid import UUID

from .core import NotionObject, TypedObject


class UserType(str, Enum):
    """Available user types."""

    PERSON = "person"
    BOT = "bot"


class User(TypedObject):
    """Represents a User in Notion."""

    object: Literal["user"] = "user"
    id: Optional[UUID] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class Person(User, type="person"):
    """Represents a Person in Notion."""

    class _NestedData(NotionObject):
        email: str

    person: _NestedData = None

    def __str__(self):
        """Return a string representation of this `Person`."""
        return f"[@{self.name}]"


class Bot(User, type="bot"):
    """Represents a Bot in Notion."""

    class _NestedData(NotionObject):
        pass

    bot: _NestedData = None

    def __str__(self):
        """Return a string representation of this `Bot`."""
        return f"[%{self.name}]"
