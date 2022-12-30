"""Unit tests for Notional core objects."""

import logging
from enum import Enum
from typing import List

import pytest

from notional.core import GenericObject, NotionObject, TypedObject

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


class Actor(NotionObject):
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


class ComplexGenericObject(TypedObject, type="detail"):
    """A complex object (with nested data) used for testing only."""

    class _NestedData(GenericObject):
        key: str = None
        value: str = None

    id: str
    detail: _NestedData = _NestedData()
    simple: List[Person] = []
    custom: CustomTypes = None


def test_parse_named_object():
    """Parse obects from structured data."""

    stan = Person.parse_obj(BOB)
    assert stan.object == "person"

    stan = Robot.parse_obj(STAN)
    assert stan.object == "robot"


def test_invalid_named_object():
    """Make sure that parsing the wrong objects raise an error."""

    with pytest.raises(ValueError):
        Robot.parse_obj(BOB)

    with pytest.raises(ValueError):
        Person.parse_obj(STAN)


def test_parse_typed_data_object():
    """Parse TypedObject's from structured data."""

    tiger = Animal.parse_obj(TIGER)
    assert type(tiger) == Cat
    assert tiger.type == "cat"
    assert tiger.name == "Tiger the Cat"
    assert not tiger.hairless

    fluffy = Animal.parse_obj(FLUFFY)
    assert type(fluffy) == Dog
    assert fluffy.type == "dog"
    assert fluffy.name == "Fluffy the Dog"
    assert fluffy.breed == "rottweiler"

    ace = Animal.parse_obj(ACE)
    assert type(ace) == Eagle
    assert ace.type == "eagle"
    assert ace.age == 245
    assert ace.species == "bald"

    # silly test just to make sure...
    assert tiger != fluffy

    bob = Person.parse_obj(BOB)
    assert bob.name == "Bob the Person"

    # make sure the Animals were deserialized correctly...
    for pet in bob.pets:
        assert pet in [fluffy, tiger]


def test_set_default_type_for_new_objects():
    """Verify that "type" is set when creating new TypedObject's."""
    bruce = Dog(name="bruce", age=3, breed="collie")
    assert bruce.type == "dog"


def test_standard_nested_object():
    """Create a nested object and check fields for proper values."""
    detail = ComplexGenericObject._NestedData(key="foo", value="bar")
    complex = ComplexGenericObject(id="complex", detail=detail)

    assert complex.id == "complex"
    assert complex.detail.key == "foo"
    assert complex.detail.value == "bar"


def test_invalid_nested_field_call():
    """Check for errors when we call for an invalid nested field."""
    complex = ComplexGenericObject(id="complex")

    with pytest.raises(AttributeError):
        complex("does_not_exist")


def test_get_nested_data():
    """Call a block to return the nested data."""
    complex = ComplexGenericObject(id="complex")

    assert complex("value") is None

    detail = complex()
    detail.value = "bar"

    assert complex.detail.key is None
    assert complex.detail.value == "bar"
