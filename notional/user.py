"""Wrapper for Notion User objects."""

import logging
from enum import Enum
from typing import Optional
from uuid import UUID

from .core import DataObject, NestedObject

log = logging.getLogger(__name__)


class UserType(str, Enum):
    """Available user types."""

    PERSON = "person"
    BOT = "bot"


class User(DataObject):
    """Represents a User in Notion."""

    id: UUID
    object: str = "user"
    type: Optional[UserType] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

    @classmethod
    def parse_obj(cls, obj):
        if obj is None:
            return None

        if "type" in obj:
            if obj["type"] == "person":
                return Person(**obj)

            if obj["type"] == "bot":
                return Bot(**obj)

        return cls(obj)


class Person(User):
    """Represents a Person in Notion."""

    class NestedData(NestedObject):
        email: str

    person: NestedData = None

    def __str__(self):
        return f"[@{self.name}]"


class Bot(User):
    """Represents a Bot in Notion."""

    class NestedData(NestedObject):
        pass

    bot: NestedData = None

    def __str__(self):
        return f"[%{self.name}]"
