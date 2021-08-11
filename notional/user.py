"""Wrapper for Notion User objects."""

import logging

from .core import TypedObject, NestedObject

log = logging.getLogger(__name__)


class User(TypedObject):
    """Represents a User in Notion."""

    object: str = "user"
    id: str = None
    name: str = None
    avatar_url: str = None


class Person(User):
    """Represents a Person in Notion."""

    class NestedPerson(NestedObject):
        email: str

    type: str = "person"
    person: NestedPerson = None

    def __getitem__(self, key):
        return self.person[key]


class Bot(User):
    """Represents a Bot in Notion."""

    class NestedBot(NestedObject):
        pass

    type: str = "bot"
    bot: NestedBot = None

    def __getitem__(self, key):
        return self.bot[key]
