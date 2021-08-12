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

ACE = """{
  "type": "eagle",
  "age": 245,
  "color": "gray",
  "species": "bald"
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


class Person(DataObject):

    name: str
    pets: List[Pet] = None


class CustomTypes(str, Enum):

    TYPE_ONE = "one"
    TYPE_TWO = "two"
    TYPE_THREE = "three"


class ComplexDataObject(DataObject):
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

        tiger = Animal.parse_raw(TIGER)
        self.assertEqual(type(tiger), Cat)
        self.assertEqual(tiger.type, "cat")
        self.assertEqual(tiger.name, "Tiger the Cat")
        self.assertFalse(tiger.hairless)

        fluffy = Animal.parse_raw(FLUFFY)
        self.assertEqual(type(fluffy), Dog)
        self.assertEqual(fluffy.type, "dog")
        self.assertEqual(fluffy.name, "Fluffy the Dog")
        self.assertEqual(fluffy.breed, "rottweiler")

        ace = Animal.parse_raw(ACE)
        self.assertEqual(type(ace), Eagle)
        self.assertEqual(ace.type, "eagle")
        self.assertEqual(ace.age, 245)
        self.assertEqual(ace.species, "bald")

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
