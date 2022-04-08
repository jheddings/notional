"""Unit tests for Notional core objects."""

import logging
import unittest
from enum import Enum
from typing import List

from notional.core import NamedObject, NestedObject, TypedObject

# keep logging output to a minumim for testing
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

ALICE = {"object": "person", "name": "Alice the Person"}

BOB = {"object": "person", "name": "Bob the Person", "pets": [TIGER, FLUFFY]}

STAN = {"name": "Stanley"}


class Actor(NamedObject):
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


class ComplexDataObject(TypedObject, type="nested"):
    """A complex object (with nested data) used for testing only."""

    class _NestedData(NestedObject):
        key: str = None
        value: str = None

    id: str
    nested: _NestedData = _NestedData()
    simple: List[Person] = []
    custom: CustomTypes = None


class DataObjectTests(unittest.TestCase):
    """Unit tests for the DataObject API objects."""

    def test_parse_basic_object(self):
        """Parse DataObject's from structured data to simulate the Notion API."""
        person = Person.parse_obj(ALICE)
        self.assertEqual(person.name, "Alice the Person")
        self.assertIsNone(person.pets)


class NamedObjectTests(unittest.TestCase):
    """Unit tests for named API objects."""

    def test_parse_named_object(self):
        """Parse NamedObject's from structured data to simulate the Notion API."""
        stan = Person.parse_obj(STAN)
        self.assertEqual(stan.object, "person")

        stan = Robot.parse_obj(STAN)
        self.assertEqual(stan.object, "robot")


class TypedObjectTests(unittest.TestCase):
    """Unit tests for typed API objects."""

    def test_parse_typed_data_object(self):
        """Parse TypedObject's from structured data to simulate the Notion API."""
        tiger = Animal.parse_obj(TIGER)
        self.assertEqual(type(tiger), Cat)
        self.assertEqual(tiger.type, "cat")
        self.assertEqual(tiger.name, "Tiger the Cat")
        self.assertFalse(tiger.hairless)

        fluffy = Animal.parse_obj(FLUFFY)
        self.assertEqual(type(fluffy), Dog)
        self.assertEqual(fluffy.type, "dog")
        self.assertEqual(fluffy.name, "Fluffy the Dog")
        self.assertEqual(fluffy.breed, "rottweiler")

        ace = Animal.parse_obj(ACE)
        self.assertEqual(type(ace), Eagle)
        self.assertEqual(ace.type, "eagle")
        self.assertEqual(ace.age, 245)
        self.assertEqual(ace.species, "bald")

        # silly test just to make sure...
        self.assertNotEqual(tiger, fluffy)

        bob = Person.parse_obj(BOB)
        self.assertEqual(bob.name, "Bob the Person")

        # make sure the Animals were deserialized correctly...
        for pet in bob.pets:
            self.assertIn(pet, [fluffy, tiger])

    def test_set_default_type_for_new_objects(self):
        """Verify that "type" is set when creating new TypedObject's."""
        bruce = Dog(name="bruce", age=3, breed="collie")
        self.assertEqual(bruce.type, "dog")


class NestedObjectTest(unittest.TestCase):
    """Test nested objects in complex data classes."""

    def test_standard_nested_object(self):
        """Create a nested object and check fields for proper values."""
        nested = ComplexDataObject._NestedData(key="foo", value="bar")
        complex = ComplexDataObject(id="complex", nested=nested)

        self.assertEqual(complex.id, "complex")
        self.assertEqual(complex.nested.key, "foo")
        self.assertEqual(complex.nested.value, "bar")

    def test_invalid_nested_field_call(self):
        """Check for errors when we call for an invalid nested field."""
        complex = ComplexDataObject(id="complex")

        with self.assertRaises(AttributeError):
            complex("does_not_exist")

    def test_get_nested_data(self):
        """Call a block to return the nested data."""
        complex = ComplexDataObject(id="complex")

        self.assertIsNone(complex("value"))

        nested = complex()
        nested.value = "bar"

        self.assertIsNone(complex.nested.key)
        self.assertEqual(complex.nested.value, "bar")
