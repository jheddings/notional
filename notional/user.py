"""Wrapper for Notion User objects."""

import logging

from .core import DataObject, NestedObject

log = logging.getLogger(__name__)


class User(DataObject):
    """Represents a User in Notion."""

    object: str = "user"
    id: str = None
    type: str = None
    name: str = None
    avatar_url: str = None


class Person(User):
    """Represents a Person in Notion."""

    class NestedPerson(NestedObject):
        email: str

    person: NestedPerson = None

    def __post_init__(self):
        self.type = "person"

    def __getitem__(self, key):
        return self.person[key]


class Bot(User):
    """Represents a Bot in Notion."""

    class NestedBot(NestedObject):
        pass

    bot: NestedBot = None

    def __post_init__(self):
        self.type = "bot"

    def __getitem__(self, key):
        return self.bot[key]
