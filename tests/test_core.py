"""Unit tests for Notional core objects."""

import logging
from enum import Enum
from typing import Any, List, Optional

import pytest
from pydantic import Field

from notional.core import DataObject, NotionObject, TypedObject

# keep logging output to a minimum for testing
logging.basicConfig(level=logging.INFO)


TIGER = {"type": "cat", "name": "Tiger the Cat", "color": "tabby", "age": 9}

FLUFFY = {
    "type": "dog",
    "name": "Fluffy the Dog",
    "color": "brown",
    "age": 3,
    "breed": "rottweiler",
}

ACE = {"type": "eagle", "age": 245, "color": "gray", "species": "bald"}

ALICE = {
    "id": "5e3204b7-f2d8-496c-876f-7db2d16e5805",
    "object": "person",
    "name": "Alice the Person",
}

BOB = {
    "id": "e9de0b88-5ace-47e9-b569-1a8b01569e21",
    "object": "person",
    "name": "Bob the Person",
    "pets": [TIGER, FLUFFY],
}

STAN = {
    "id": "1e0042be-9407-4064-9bea-ecdcf6c2d78b",
    "object": "robot",
    "name": "Stanley",
}


class Actor(DataObject):
    """A structured Actor class for testing."""

    name: str


class Animal(TypedObject):
    """A structured Animal class for testing."""

    age: int
    color: str = None


class Pet(Animal):
    """A structured Pet class for testing."""

    name: str


class Cat(Pet, type="cat"):
    """A structured Cat class for testing."""

    hairless: bool = False


class Dog(Pet, type="dog"):
    """A structured Dog class for testing."""

    breed: str


class Eagle(Animal, type="eagle"):
    """A structured Eagle class for testing."""

    species: str


class Person(Actor, object="person"):
    """A structured Person class for testing."""

    pets: List[Pet] = None


class Robot(Actor, object="robot"):
    """A structured Robot class for testing."""


class CustomTypes(str, Enum):
    """Defines custom types for testing."""

    TYPE_ONE = "one"
    TYPE_TWO = "two"
    TYPE_THREE = "three"


class ComplexObject(TypedObject, type="detail"):
    """A complex object (with nested data) used for testing only."""

    class _NestedData(NotionObject):
        key: str = None
        value: str = None

    id: str
    detail: _NestedData = Field(default_factory=_NestedData)
    simple: List[Person] = []
    custom: CustomTypes = None


class PrivateDataObject(NotionObject):
    """An object that uses properties to access data."""

    _private: Optional[Any] = None

    @property
    def InternalData(self):
        """Return the private data of this object."""
        return self._private

    @InternalData.setter
    def InternalData(self, value):
        """Set the private data of this object."""
        self._private = value


def test_parse_named_object():
    """Parse obects from structured data."""

    bob = Person.deserialize(BOB)
    assert bob.object == "person"

    stan = Robot.deserialize(STAN)
    assert stan.object == "robot"


def test_parse_typed_data_object():
    """Parse TypedObject's from structured data."""

    tiger = Animal.deserialize(TIGER)
    assert type(tiger) == Cat
    assert tiger.type == "cat"
    assert tiger.name == "Tiger the Cat"
    assert not tiger.hairless

    fluffy = Animal.deserialize(FLUFFY)
    assert type(fluffy) == Dog
    assert fluffy.type == "dog"
    assert fluffy.name == "Fluffy the Dog"
    assert fluffy.breed == "rottweiler"

    ace = Animal.deserialize(ACE)
    assert type(ace) == Eagle
    assert ace.type == "eagle"
    assert ace.age == 245
    assert ace.species == "bald"

    # silly test just to make sure...
    assert tiger != fluffy

    bob = Person.deserialize(BOB)
    assert bob.name == "Bob the Person"

    # make sure the Animals were deserialized correctly...
    for pet in bob.pets:
        assert pet in [fluffy, tiger]


def test_mixing_object_types():
    """Make sure that parsing the wrong objects returns the correct type."""

    # because subclasses of a type tree share the typemap, trying to
    # parse as the "wrong" class should return the correct class instead

    fluffy = Cat.deserialize(FLUFFY)
    assert isinstance(fluffy, Dog)

    tiger = Dog.deserialize(TIGER)
    assert isinstance(tiger, Cat)


def test_set_default_type_for_new_objects():
    """Verify that "type" is set when creating new TypedObject's."""
    bruce = Dog(name="bruce", age=3, breed="collie")
    assert bruce.type == "dog"


def test_standard_nested_object():
    """Create a nested object and check fields for proper values."""
    detail = ComplexObject._NestedData(key="foo", value="bar")
    complex = ComplexObject(id="complex", detail=detail)

    assert complex.id == "complex"
    assert complex.detail.key == "foo"
    assert complex.detail.value == "bar"


def test_invalid_nested_field_call():
    """Check for errors when we call for an invalid nested field."""
    complex = ComplexObject(id="complex")

    with pytest.raises(AttributeError):
        complex("does_not_exist")


def test_get_nested_data():
    """Call a block to return the nested data."""
    complex = ComplexObject(id="complex")

    assert complex("value") is None

    detail = complex()
    detail.value = "bar"

    assert complex.detail.key is None
    assert complex.detail.value == "bar"


def test_split_typemap():
    """Verify AdaptiveObject's behave when different typemaps use the same key."""


def test_property_setter():
    """Verify property setter funcionality.

    This was initially fixed in `notional.NotionObject`, however later versions of Pydantic
    added support for property setters.  We may remove this test in the future.

    Ref: https://github.com/pydantic/pydantic/issues/1577
    """

    private = PrivateDataObject()
    assert private.InternalData is None

    private.InternalData = "Sup3Rs3ç4é†"
    assert private.InternalData == "Sup3Rs3ç4é†"


tiger = Animal.deserialize(TIGER)

print(tiger)
