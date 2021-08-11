import logging
import unittest
from enum import Enum
from typing import Dict, List

from notional.core import DataObject, NestedObject, TypedObject

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


TIGER = """{
  "type": "cat",
  "name": "Tiger the Cat",
  "color": "tabby",
  "age": 9
}"""


FLUFFY = """{
  "type": "dog",
  "name": "Fluffy the Dog",
  "color": "brown",
  "age": 3,
  "breed": "rottweiler"
}"""


ALICE = """{
  "name": "Alice the Person"
}"""


BOB = f"""{{
  "name": "Bob the Person",
  "pets": [
    {TIGER},{FLUFFY}
  ]
}}"""


class Animal(TypedObject):
    """Basic data for a TypedObject."""

    name: str
    age: int
    color: str = None


class Cat(Animal, type="cat"):
    """Additional data for a Cat."""

    hairless: bool = False


class Dog(Animal, type="dog"):
    """Additional data for a Dog."""

    breed: str


class Person(DataObject):
    """Basic data for a Person."""

    name: str
    pets: List[Animal] = None


class CustomTypes(str, Enum):
    TYPE_ONE = "one"
    TYPE_TWO = "two"
    TYPE_THREE = "three"


class ComplexDataObject(DataObject):
    """Represents a complex data object from the API."""

    class NestedData(NestedObject):
        key: str
        value: str = None

    id: str
    nested: NestedData = None
    simple: List[Person] = []
    custom: CustomTypes = None


class DataObjectTest(unittest.TestCase):
    """Unit tests for the DataObject API objects."""

    def test_ParseDataObject(self):
        """Basic DataObject parsing."""

        person = Person.parse_raw(ALICE)
        self.assertEqual(person.name, "Alice the Person")
        self.assertIsNone(person.pets)

    def test_ParseTypedDataObject(self):
        """TypedObject parsing."""

        tiger = Cat.parse_raw(TIGER)
        self.assertEqual(tiger.type, "cat")
        self.assertEqual(tiger.name, "Tiger the Cat")
        self.assertFalse(tiger.hairless)

        fluffy = Dog.parse_raw(FLUFFY)
        self.assertEqual(fluffy.type, "dog")
        self.assertEqual(fluffy.name, "Fluffy the Dog")
        self.assertEqual(fluffy.breed, "rottweiler")

        # silly test just to make sure...
        self.assertNotEqual(tiger, fluffy)

        bob = Person.parse_raw(BOB)
        self.assertEqual(bob.name, "Bob the Person")

        # make sure the Animals were deserialized correctly...
        for pet in bob.pets:
            self.assertIn(pet, [fluffy, tiger])

    def test_ParseComplexDataObject(self):
        """Complex DataObject parsing."""
        pass
