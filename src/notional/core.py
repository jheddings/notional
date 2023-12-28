"""Base classes for working with the Notion API."""

import logging
from abc import ABC
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, ValidationError, model_validator
from pydantic._internal._model_construction import ModelMetaclass
from pydantic_core import PydanticCustomError

# https://github.com/pydantic/pydantic/issues/6381
# https://github.com/pydantic/pydantic/discussions/7008

logger = logging.getLogger(__name__)


_T = TypeVar("_T")


class SerializationMode(str, Enum):
    """Serialization mode for Notional objects."""

    JSON = "json"
    PYTHON = "python"
    API = PYTHON


class ComposableObjectMeta(ModelMetaclass):
    """Presents a metaclass that composes objects using simple values.

    This is primarily to allow easy definition of data objects without disrupting the
    `BaseModel` constructor.  e.g. rather than requiring a caller to understand how
    nested data works in the data objects, they can compose objects from simple values.

    Compare the following code for declaring a Paragraph:

    ```python
    # using nested data objects:
    text = "hello world"
    nested = TextObject._NestedData(content=text)
    rtf = text.TextObject(text=nested, plain_text=text)
    content = blocks.Paragraph._NestedData(text=[rtf])
    para = blocks.Paragraph(paragraph=content)

    # using a composable object:
    para = blocks.Paragraph["hello world"]
    ```

    Classes that support composition in this way must define and implement the internal
    `__compose__` method.  This method takes an arbitrary number of parameters, based
    on the needs of the implementation.  It is up to the implementing class to ensure
    that the parameters are specified correctly.
    """

    def __getitem__(cls: type[_T], params: Any) -> _T:
        """Return the requested class by composing using the given parameters.

        If the requested class does not expose the `__compose__` method, this will raise
        an exception.
        """

        compose: Callable[[Dict[str, Any]], _T] = getattr(cls, "__compose__", None)

        if compose is None:
            raise NotImplementedError(f"{cls} does not support object composition")

        # __getitem__ only accepts a single parameter...  if the caller provides
        # multiple params, they will be converted and passed as a tuple.  this method
        # also accepts a list for readability when composing from ORM properties

        if params and type(params) in (list, tuple):
            return compose(*params)

        return compose(params)


class NotionObject(BaseModel, ABC, metaclass=ComposableObjectMeta):
    """The base for all Notion API objects.

    As a general convention, data fields in lower case are defined by the Notion API.
    Properties in Title Case are provided for convenience (e.g. computed fields).
    """

    def update(self, **data):
        """Refresh the internal attributes with new data."""

        # ref: https://github.com/pydantic/pydantic/discussions/3139

        partial_model = self.model_validate(data)

        for name in data.keys():
            if not hasattr(partial_model, name):
                raise AttributeError(f"{type(partial_model)}: {name}", name=name)

            value = getattr(partial_model, name)

            logger.debug("update object -- %s => %s", name, value)
            setattr(self, name, value)

        return self

    def serialize(self, mode: SerializationMode = SerializationMode.API):
        """Convert to a suitable representation for the Notion API."""

        # TODO read-only fields should not be sent to the API
        # https://github.com/jheddings/notional/issues/9

        if mode == SerializationMode.PYTHON:
            return self.model_dump(mode="json", exclude_none=True, by_alias=True)

        if mode == SerializationMode.JSON:
            return self.model_dump_json(indent=None, exclude_none=True, by_alias=True)

        raise NotImplementedError(f"unsupported serialization mode: {mode}")

    @classmethod
    def deserialize(cls, data: Union[str, bytes, dict, list]):
        """Parse the given object as a Notion API object."""

        if isinstance(data, (str, bytes)):
            return cls.model_validate_json(data)

        return cls.model_validate(data)


class AdaptiveObject(NotionObject, ABC):
    """An abstract object that may be one of several concrete types.

    To determine the concrete type of an API object, AdaptiveObject's will examine all
    available subclasses of the requested class and attempt to validate the given data.
    The first object that successfully validates will be created and returned.

    This approach allows objects to contain similar fields without causing conflicts
    during resolution.  For example, a `Person` object may contain a `name` field, but a
    `Pet` object may also contain a `name` field.  If the `Person` object is requested,
    the `Pet` object will not be considered for resolution.
    """

    @model_validator(mode="wrap")
    @classmethod
    def _resolve_adaptive_object(cls, data: dict, handler) -> Any:
        if not isinstance(data, dict):
            return handler(data)

        # if cls is not abstract, there's nothing to do
        if ABC not in cls.__bases__:
            return handler(data)

        # try to validate the data for each possible type
        for subcls in cls._find_all_possible_types():
            try:
                obj = subcls.model_validate(data)
            except ValidationError:
                continue

            logger.debug("deserialized '%s' as '%s'", cls, subcls)

            return obj

        raise PydanticCustomError(
            "adaptive-object",
            "unable to resolve input",
        )

    @classmethod
    def _find_all_possible_types(cls):
        """Recursively generate all possible types for this object.

        Possible types include this class or any of its subclasses that are not
        abstract.
        """

        # any concrete subclass is a possible type
        if ABC not in cls.__bases__:
            yield cls

        # continue looking for possible types in subclasses
        for subclass in cls.__subclasses__():
            yield from subclass._find_all_possible_types()


class DataObject(AdaptiveObject, ABC):
    """A top-level Notion data object."""

    object: str
    id: Optional[UUID] = None


class TypedObject(AdaptiveObject, ABC):
    """A type-referenced object.

    Many objects in the Notion API follow a standard pattern with a 'type' property
    followed by additional data.  These objects must specify a `type` attribute to
    ensure that the correct object is created.

    For example, this contains a nested 'detail' object:

        data = {
            type: "detail",
            ...
            detail: {
                ...
            }
        }

    Calling the object provides direct access to the data stored in `{type}`.
    """

    type: str

    def __call__(self, field: Optional[str] = None) -> Any:
        """Return the nested data object contained by this `TypedObject`.

        If a field is provided, the contents of that field in the nested data will be
        returned.  Otherwise, the full contents of the NestedData will be returned.
        """

        type = getattr(self, "type", None)

        if type is None:
            raise AttributeError("type not specified", name="type")

        if not hasattr(self, type):
            raise AttributeError(f"missing nested data: {type}", name=type)

        nested = getattr(self, type)

        if field is not None and nested is not None:
            nested = getattr(nested, field)

        return nested
