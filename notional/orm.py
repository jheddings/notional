"""Utilities for working with Notion as an ORM."""

import logging
from abc import ABC

from .records import DatabaseRef, Page
from .types import NativeTypeMixin, RichText

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
                           with format `name: value` where `name` is the attribute in
                           the custom type and `value` is a supported type for composing
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


def Property(name, cls=RichText, default=None):
    """Define a property for a Notion Page object.

    :param name: the Notion table property name
    :param cls: the data type for the property (default = RichText)
    :param default: a default value when creating new objects
    """

    log.debug("creating new Property: %s", name)

    def fget(self):
        """Return the current value of the property as a python object."""

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        log.debug("getter %s [%s]", cls, name)

        try:
            prop = self.page[name]
        except AttributeError:
            return default

        if not isinstance(prop, cls):
            raise TypeError("Type mismatch")

        # convert native objects to expected types
        if isinstance(prop, NativeTypeMixin):
            return prop.Value

        return prop

    def fset(self, value):
        """Set the property to the given value."""

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        log.debug("setter %s [%s] => %s %s", cls, name, value, type(value))

        if isinstance(value, cls):
            prop = value

        elif hasattr(cls, "__compose__"):
            prop = cls.__compose__(value)

        else:
            raise ValueError(f"Value does not match expected type: {cls}")

        # update the local property
        self.page[name] = prop

        # update the property live on the server
        self._orm_session_.pages.update(self.page, **{name: prop})

    return property(fget, fset)


def connected_page(session=None, cls=ConnectedPageBase):
    """Return a base class for "connected" pages through the Notion API.

    Subclasses may then inherit from the returned class to define custom ORM types.

    :param session: an active Notional session where the database is hosted
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
