"""Wrapper for Notion User objects."""

import logging
from dataclasses import dataclass

from .core import DataObject, NestedObject

log = logging.getLogger(__name__)


@dataclass
class User(DataObject):
    """Represents a User in Notion."""

    object: str = "user"
    id: str = None
    type: str = None
    name: str = None
    avatar_url: str = None

    @classmethod
    def from_json(cls, data):
        """Override the default method to provide a factory for subclass types."""

        # prevent infinite loops from subclasses...
        if cls == User:
            data_type = data.get("type")

            if data_type == "person":
                return Person.from_json(data)

            if data_type == "bot":
                return Bot.from_json(data)

        return super().from_json(data)


@dataclass
class Person(User):
    """Represents a Person in Notion."""

    @dataclass
    class NestedPerson(NestedObject):
        email: str

    person: NestedPerson = None

    def __post_init__(self):
        self.type = "person"

    def __getitem__(self, key):
        return self.person[key]


@dataclass
class Bot(User):
    """Represents a Bot in Notion."""

    @dataclass
    class NestedBot(NestedObject):
        pass

    bot: NestedBot = None

    def __post_init__(self):
        self.type = "bot"

    def __getitem__(self, key):
        return self.bot[key]
