"""Utilities for working with Notion as an ORM."""

import logging
from abc import ABC

from .records import DatabaseRef, Page
from .schema import PropertyObject, RichText
from .types import PropertyValue

log = logging.getLogger(__name__)


class ConnectedPageBase(ABC):
    """Base class for "live" pages via the Notion API.

    All changes are committed in real time.
    """

    def __init__(self, **data):
        """Construct a page from the given data dictionary."""
        self.__page_data__ = Page(**data) if data else None

    @property
    def id(self):
        """Return the ID of this page (if available)."""
        return self.__page_data__.id if self.__page_data__ else None

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""

        if self.__page_data__ is None:
            return []

        return self._orm_session_.blocks.children.list(parent=self.__page_data__)

    def __iadd__(self, block):
        """Append the given block to this page.

        This operation takes place on the Notion server, causing the page to save
        immediately.
        """

        self.append(block)

        return self

    def append(self, *blocks):
        """Append the given blocks as children of this ConnectedPage.

        This operation takes place on the Notion server, causing the page to update
        immediately.
        """

        if self.__page_data__ is None:
            raise ValueError("Cannote append blocks; missing page")

        if self._orm_session_ is None:
            raise ValueError("Cannote append blocks; invalid session")

        log.debug(
            "appending %d blocks to page :: %s", len(blocks), self.__page_data__.id
        )
        self._orm_session_.blocks.children.append(self.__page_data__, *blocks)

    @classmethod
    def create(cls, **kwargs):
        """Create a new instance of the ConnectedPage type.

        Any properties that support object composition may defined in `kwargs`.

        This operation takes place on the Notion server, creating the page immediately.

        :param properties: the properties to initialize for this object as a `dict()`
          with format `name: value` where `name` is the attribute in the custom type
          and `value` is a supported type for composing
        """

        if cls._orm_session_ is None:
            raise ValueError("Cannote create Page; invalid session")

        log.debug("creating new %s :: %s", cls, cls._orm_database_id_)

        parent = DatabaseRef(database_id=cls._orm_database_id_)

        connected = cls()
        connected.__page_data__ = cls._orm_session_.pages.create(parent=parent)

        # FIXME it would be better to convert properties to a dict and pass to the API,
        # rather than setting them individually here...
        for name, value in kwargs.items():
            setattr(connected, name, value)

        return connected

    @classmethod
    def parse_obj(cls, data):
        """Invoke the class constructor using the structured data.

        Similar to `BaseModel.parse_obj(data)`.
        """
        return cls(**data)


class _ConnectedPropertyWrapper:
    """Contains the information and methods needed for a connected property."""

    def __init__(self, name, schema, default=...):
        """Initialize the property wrapper."""

        if name is None or len(name) == 0:
            raise ValueError("Must provide a valid property name")

        if schema is None:
            raise ValueError("Invalid schema; cannot be None")

        self.name = name
        self.default = default
        self.schema = schema
        self.data_type = type(schema)

        if not hasattr(self.data_type, "type") or self.data_type.type is None:
            raise ValueError("Invalid schema; undefined type")

        self.type_name = self.data_type.type

        # this is kind of an ugly way to grab the value type from the schema type...
        # mostly b/c we are using internal knowledge of TypedObject.__typemap__
        if self.type_name not in PropertyValue.__typemap__:
            raise TypeError(f"Invalid schema; missing value type '{self.type_name}'")

        self.value_type = PropertyValue.__typemap__[self.type_name]

    def bind(self, obj):
        """Binds this property to the given object."""

        if not isinstance(obj, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        # XXX should we do any additional error checking on the object?

        self.parent = obj
        self.page_data = self.parent.__page_data__
        self.session = self.parent._orm_session_

    def get(self):
        """Return the current value of the property as a python object."""
        log.debug("fget :: %s [%s]", self.type_name, self.name)

        # TODO raise instead?
        if self.page_data is None:
            return None

        try:
            prop = self.page_data[self.name]
        except AttributeError:
            if self.default == ...:
                raise AttributeError(f"Missing property: '{self.name}'")
            return self.default

        if not isinstance(prop, self.value_type):
            raise TypeError("Type mismatch")

        if hasattr(prop, "Value"):
            return prop.Value

        return prop

    def set(self, value):
        """Set the property to the given value."""
        log.debug("fset :: %s [%s] => %s", self.type_name, self.name, type(value))

        # TODO raise instead?
        if self.page_data is None:
            return None

        if isinstance(value, self.value_type):
            prop = value

        elif hasattr(self.value_type, "__compose__"):
            prop = self.value_type.__compose__(value)

        else:
            raise TypeError(f"Unsupported value type for '{self.type_name}'")

        # update the property on the server (which will refresh the local data)
        self.session.pages.update(self.page_data, **{self.name: prop})

    def delete(self):
        """Delete the value assotiated with this property."""

        # TODO raise instead?
        if self.page_data is None:
            return None

        empty = self.value_type()

        self.session.pages.update(self.page_data, **{self.name: empty})


def Property(name, schema=None, default=...):
    """Define a property for a Notion Page object.

    :param name: the Notion table property name
    :param data_type: the schema that defines this property (default = RichText)
    :param default: a default value when creating new objects
    """

    log.debug("creating new Property: %s", name)

    if schema is None:
        schema = RichText()

    elif not isinstance(schema, PropertyObject):
        raise TypeError("Invalid data_type; not a PropertyObject")

    cprop = _ConnectedPropertyWrapper(
        name=name,
        schema=schema,
        default=default,
    )

    def fget(self):
        """Return the current value of the property as a python object."""
        cprop.bind(self)
        return cprop.get()

    def fset(self, value):
        """Set the property to the given value."""
        cprop.bind(self)
        cprop.set(value)

    def fdel(self):
        """Delete the value for this property."""
        cprop.bind(self)
        cprop.delete()

    return property(fget, fset, fdel)


def connected_page(session=None, cls=ConnectedPageBase):
    """Return a base class for "connected" pages through the Notion API.

    Subclasses may then inherit from the returned class to define custom ORM types.

    :param session: an active Notional session where the database is hosted

    :param database: if provided, the returned class will use the ID and schema of
      this object to initialize the connected page

    :param schema: if provided, the returned class will contain properties according
      to the schema provided
    """

    if not issubclass(cls, ConnectedPageBase):
        raise ValueError("cls must subclass ConnectedPageBase")

    class _ConnectedPage(cls):
        """Base class for all connected pages, which serve as the basis for ORM types.

        In particular, this class holds the connection information for an active
        Notional session.  This session is used by `ConnectedPageBase` to perform API
        actions.
        """

        _orm_database_ = None
        _orm_database_id_ = None
        _orm_session_ = None
        _orm_late_bind_ = None

        def __init_subclass__(cls, database=None, **kwargs):
            """Attach the ConnectedPage to the given database ID.

            Alternatively, a class may specify the database ID with an internal
            `__database__` attribute.
            """
            super().__init_subclass__(**kwargs)

            if cls._orm_database_id_ is not None:
                raise TypeError(f"Object {cls} registered to: {database}")

            if database:
                cls._orm_database_id_ = database

            elif hasattr(cls, "__database__"):
                cls._orm_database_id_ = cls.__database__

            else:
                raise ValueError(f"Missing 'database' for ConnectedPage: {cls}")

            # if the local session is None, we will use _orm_bind_session_
            cls.bind(session or cls._orm_late_bind_)

            log.debug("registered connected page :: %s => %s", cls, database)

        @classmethod
        def bind(cls, to_session):
            """Attach this ConnectedPage to the given session.

            Setting this to None will detach the page.
            """

            cls._orm_late_bind_ = to_session
            cls._orm_session_ = to_session

    return _ConnectedPage
