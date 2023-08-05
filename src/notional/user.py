"""Wrapper for Notion user objects."""

from abc import ABC
from enum import Enum
from typing import Literal, Optional

from .core import DataObject, NotionObject, TypedObject


class UserType(str, Enum):
    """Available user types."""

    PERSON = "person"
    BOT = "bot"


class PartialUser(DataObject):
    """Represents a partial User in Notion."""

    object: Literal["user"] = "user"


class User(PartialUser, TypedObject, ABC):
    """Represents a User in Notion."""

    name: Optional[str] = None
    avatar_url: Optional[str] = None


class Person(User):
    """Represents a Person in Notion."""

    class _NestedData(NotionObject):
        email: str

    person: _NestedData
    type: Literal["person"] = "person"

    def __str__(self) -> str:
        """Return a string representation of this `Person`."""
        return f"[@{self.name}]"


class BotOwner(TypedObject):
    """Represents a Bot Owner in Notion."""

    workspace: bool = False
    type: Literal["user", "workspace"]


class Bot(User):
    """Represents a Bot in Notion."""

    class _NestedData(NotionObject):
        owner: Optional[BotOwner] = None
        workspace_name: Optional[str] = None

    bot: _NestedData
    type: Literal["bot"] = "bot"

    def __str__(self) -> str:
        """Return a string representation of this `Bot`."""
        return f"[%{self.name}]"
