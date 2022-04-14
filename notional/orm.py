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
        self.page = Page(**data) if data else None
        self._pending_props = {}

    @property
    def id(self):
        """Return the ID of this page (if available)."""
        return self.page.id if self.page else None

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""

        if self.page is None:
            return []

        return self._orm_session_.blocks.children.list(parent=self.page)

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

        if self.page is None:
            raise ValueError("Cannote append blocks; missing page")

        if self._orm_session_ is None:
            raise ValueError("Cannote append blocks; invalid session")

        log.debug("appending %d blocks to page :: %s", len(blocks), self.page.id)
        self._orm_session_.blocks.children.append(self.page, *blocks)

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
        connected.page = cls._orm_session_.pages.create(parent=parent)

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

    def __init__(self, name, schema, default):
        self.name = name
        self.schema = schema
        self.default = default

        if name is None or len(name) == 0:
            raise AttributeError("Must provide a valid property name")

        if schema is None:
            raise AttributeError("Invalid schema; cannot be None")

        self.data_type = type(schema)

        if not hasattr(self.data_type, "type") or self.data_type.type is None:
            raise AttributeError("Invalid schema; undefined type")

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

        self.page = obj.page
        self.session = obj._orm_session_

    def getter(self):
        """Return the current value of the property as a python object."""
        log.debug("fget :: %s [%s]", self.type_name, self.name)

        try:
            prop = self.page[self.name]
        except AttributeError:
            prop = self.default

        if not isinstance(prop, self.value_type):
            raise TypeError("Type mismatch")

        # convert native objects to expected types
        if hasattr(prop, "Value"):
            return prop.Value

        return prop

    def setter(self, value):
        """Set the property to the given value."""
        log.debug("fset :: %s [%s] => %s", self.type_name, self.name, type(value))

        if isinstance(value, self.value_type):
            prop = value

        elif hasattr(self.value_type, "__compose__"):
            prop = self.value_type.__compose__(value)

        else:
            raise TypeError(f"Unsupported value type for '{self.type_name}'")

        # update the property on the server (which will refresh the local data)
        self.session.pages.update(self.page, **{self.name: prop})

    def delete(self):
        """Delete the value assotiated with this property."""
        self.session.pages.update(self.page, **{self.name: None})


def Property(name, schema=None, default=None):
    """Define a property for a Notion Page object.

    :param name: the Notion table property name
    :param data_type: the schema that defines this property (default = RichText)
    :param default: a default value when creating new objects
    """

    log.debug("creating new Property: %s", name)

    if schema is None:
        schema = RichText()

    elif not isinstance(schema, PropertyObject):
        raise AttributeError("Invalid data_type; not a PropertyObject")

    cprop = _ConnectedPropertyWrapper(
        name=name,
        schema=schema,
        default=default,
    )

    def fget(self):
        """Return the current value of the property as a python object."""
        cprop.bind(self)
        return cprop.getter()

    def fset(self, value):
        """Set the property to the given value."""
        cprop.bind(self)
        cprop.setter(value)

    def fdel(self, value):
        """Delete the value for this property."""
        cprop.bind(self)
        cprop.delete(value)

    return property(fget, fset, fdel)


def connected_page(session=None, database=None, schema=None, cls=ConnectedPageBase):
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
