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

    name: str


class Animal(TypedObject):

    age: int
    color: str = None


class Pet(Animal):

    name: str


class Cat(Pet, type="cat"):

    hairless: bool = False


class Dog(Pet, type="dog"):

    breed: str


class Eagle(Animal, type="eagle"):

    species: str


class Person(Actor, object="person"):

    pets: List[Pet] = None


class Robot(Actor, object="robot"):

    pass


class CustomTypes(str, Enum):

    TYPE_ONE = "one"
    TYPE_TWO = "two"
    TYPE_THREE = "three"


class ComplexDataObject(TypedObject, type="nested"):
    class NestedData(NestedObject):
        key: str = None
        value: str = None

    id: str
    nested: NestedData = NestedData()
    simple: List[Person] = []
    custom: CustomTypes = None


class DataObjectTests(unittest.TestCase):
    """Unit tests for the DataObject API objects."""

    def test_ParseBasicObject(self):
        """Basic DataObject parsing."""

        person = Person.parse_obj(ALICE)
        self.assertEqual(person.name, "Alice the Person")
        self.assertIsNone(person.pets)


class NamedObjectTests(unittest.TestCase):
    """Unit tests for named API objects."""

    def test_ParseNamedObject(self):
        stan = Person.parse_obj(STAN)
        self.assertEqual(stan.object, "person")

        stan = Robot.parse_obj(STAN)
        self.assertEqual(stan.object, "robot")


class TypedObjectTests(unittest.TestCase):
    """Unit tests for typed API objects."""

    def test_ParseTypedDataObject(self):
        """TypedObject parsing."""

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

    def test_SetDefaultTypeForNewObjects(self):
        """Verify that "type" is set by default on new TypedObject's."""
        bruce = Dog(name="bruce", age=3, breed="collie")
        self.assertEqual(bruce.type, "dog")


class NestedObjectTest(unittest.TestCase):
    def test_StandardNestedObject(self):
        """Check usage of get/set items in TypedObject'."""
        nested = ComplexDataObject.NestedData(key="foo", value="bar")
        complex = ComplexDataObject(id="complex", nested=nested)

        self.assertEqual(complex.nested.value, "bar")

    def test_InvalidNestedFieldCall(self):
        complex = ComplexDataObject(id="complex")

        with self.assertRaises(AttributeError):
            complex("does_not_exist")

    def test_GetSetNestedData(self):
        """Verify we can call a block for nested data'."""
        complex = ComplexDataObject(id="complex")

        self.assertIsNone(complex("value"))

        nested = complex()
        nested.value = "bar"

        self.assertIsNone(complex.nested.key)
        self.assertEqual(complex.nested.value, "bar")
