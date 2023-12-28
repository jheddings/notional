"""Unit tests for Notional core objects."""

import json
import logging
from abc import ABC
from typing import Any, List, Literal, Optional

import pytest
from pydantic import Field, SerializeAsAny, ValidationError

from notional.core import DataObject, NotionObject, SerializationMode, TypedObject

# keep logging output to a minimum for testing
logging.basicConfig(level=logging.INFO)


TIGER = {
    "type": "cat",
    "name": "Tiger the Cat",
    "color": "tabby",
    "age": 9,
}

FLUFFY = {
    "type": "dog",
    "name": "Fluffy the Dog",
    "color": "brown",
    "age": 3,
    "breed": "rottweiler",
}

ACE = {
    "type": "bird",
    "age": 42,
    "color": "gray",
    "species": "eagle",
}

ALICE = {
    "object": "person",
    "name": "Alice the Person",
    "pets": [TIGER, FLUFFY],
}

BOB = {
    "object": "person",
    "name": "Bob the Person",
    "pets": [FLUFFY, ACE],
}

STAN = {
    "object": "robot",
    "name": "Stanley",
}


class Actor(DataObject, ABC):
    """A structured Actor class for testing."""

    name: str


class Animal(TypedObject, ABC):
    """A structured Animal class for testing."""

    age: int
    color: Optional[str] = None


class Pet(Animal, ABC):
    """A structured Pet class for testing."""

    name: str


class Cat(Pet):
    """A structured Cat class for testing."""

    hairless: bool = False
    type: Literal["cat"] = "cat"


class Dog(Pet):
    """A structured Dog class for testing."""

    breed: str
    type: Literal["dog"] = "dog"


class Bird(Animal):
    """A structured Bird class for testing."""

    species: str
    type: Literal["bird"] = "bird"


class Person(Actor):
    """A structured Person class for testing."""

    pets: List[SerializeAsAny[Pet]] = []
    object: Literal["person"] = "person"


class Robot(Actor):
    """A structured Robot class for testing."""

    object: Literal["robot"] = "robot"

    @classmethod
    def __compose__(cls, name):
        """Compose a Robot object with the given name."""
        return Robot(name=name)


class DetailedObject(TypedObject):
    """A complex object (with nested data) used for testing only."""

    class _NestedData(NotionObject):
        key: Optional[str] = None
        value: Optional[str] = None

    id: str
    simple: List[Person] = []
    detail: _NestedData = Field(default_factory=_NestedData)
    type: Literal["detail"] = "detail"


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


def test_serialize_json():
    """Serialize objects to JSON and verify contents."""

    jack = Person(name="Jack the Person")
    raw = jack.serialize(SerializationMode.JSON)

    # make sure we can parse the JSON
    data = json.loads(raw)

    assert data["object"] == "person"
    assert data["name"] == "Jack the Person"
    assert len(data["pets"]) == 0


def test_serialize_dict():
    """Serialize objects to Python objects and verify contents."""
    tiger = Cat(name="Tiger", age=9, hairless=True)
    data = tiger.serialize(SerializationMode.PYTHON)

    assert data["name"] == "Tiger"
    assert data["hairless"] is True


def test_serialize_adaptive_types():
    """Serialize objects with abstract types."""

    # objects that have fields with abstract types can be problematic
    # in this case, we have a Person with a list of Pets that should be
    # serialized as a list of concrete types

    tiger = Cat(name="Tiger", age=9, hairless=True)
    fluffy = Dog(name="Fluffy", age=4, breed="poodle")
    jill = Person(name="Jill with Pets", pets=[tiger, fluffy])

    data = jill.serialize()

    assert data["object"] == "person"
    assert data["name"] == "Jill with Pets"

    assert "pets" in data
    assert len(data["pets"]) == 2

    assert data["pets"][0] == tiger.serialize()
    assert data["pets"][1] == fluffy.serialize()


def test_parse_named_object():
    """Parse obects from structured data."""

    alice = Person.deserialize(ALICE)
    assert alice.object == "person"

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
    assert type(ace) == Bird
    assert ace.type == "bird"
    assert ace.age == 42
    assert ace.species == "eagle"

    # just to make sure...
    assert tiger != fluffy


def test_deserialize_adaptive_types():
    """Verify that adaptive types are always deserialized correctly.

    In particular, abstract types that are declared inside of a collection (e.g. a list)
    can be problematic.
    """

    alice = Person.deserialize(ALICE)
    assert alice.name == "Alice the Person"

    # make sure the Animals were deserialized correctly...
    assert alice.pets[0] == Cat.deserialize(TIGER)
    assert alice.pets[1] == Dog.deserialize(FLUFFY)

    # BOB is not a valid Person because he has a Bird as a pet
    with pytest.raises(ValidationError):
        _ = Person.deserialize(BOB)


def test_mixing_object_types():
    """Make sure that parsing the wrong objects fails."""

    with pytest.raises(ValidationError):
        Cat.deserialize(FLUFFY)

    with pytest.raises(ValidationError):
        Dog.deserialize(TIGER)


def test_invalid_nested_field_call():
    """Check for errors when we call for an invalid nested field."""
    complex = DetailedObject(id="boring_object")

    with pytest.raises(AttributeError):
        complex("does_not_exist")


def test_get_nested_data():
    """Call a block to return the nested data."""
    complex = DetailedObject(id="interactive_object")

    assert complex("value") is None

    detail = complex()
    detail.value = "bar"

    assert complex.detail.key is None
    assert complex.detail.value == "bar"

    assert complex("value") == "bar"


def test_composable_object():
    """Compose an object with a simple __compose__ method."""
    stella = Robot["Stella"]

    assert isinstance(stella, Robot)
    assert stella.name == "Stella"
    assert stella.object == "robot"


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
