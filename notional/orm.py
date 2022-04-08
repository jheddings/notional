"""Utilities for working with Notion as an ORM."""

import logging

from .iterator import EndpointIterator
from .records import DatabaseRef, Page
from .types import NativeTypeMixin, RichText

log = logging.getLogger(__name__)


class ConnectedPageBase:
    """Base class for "live" pages via the Notion API.

    All changes are committed in real time.
    """

    def __init__(self, **data):
        self.page = Page(**data) if data else None
        self._pending_props = {}

    @property
    def id(self):
        """Return the ID of this page (if available)."""

        return None if self.page is None else self.page.id

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""

        return EndpointIterator(
            endpoint=self._orm_session_.blocks.children().list, block_id=self.id
        )

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

        log.debug("appending %d blocks to page :: %s", len(blocks), self.page.id)
        self._orm_session_.blocks.children.append(self.page, *blocks)

    @classmethod
    def create(cls, **properties):
        """Creates a new instance of the ConnectedPage type.

        Any properties that support native type assignment may be set

        This operation takes place on the Notion server, causing the page to update
        immediately.
        """

        log.debug("creating new %s :: %s", cls, cls._orm_database_id_)

        parent = DatabaseRef(database_id=cls._orm_database_id_)

        # bypass the data constructor to avoid multiple copies of the page data...
        connected = cls()
        connected.page = cls._orm_session_.pages.create(parent=parent)

        # FIXME it would be better to convert properties to a dict and pass to the API,
        # rather than setting them individually here...  this is bad performance.
        for name, value in properties.items():
            setattr(connected, name, value)

        return connected

    @classmethod
    def parse_obj(cls, data):
        return cls(**data)


def Property(name, cls=RichText, default=None):
    """Define a property for a Notion Page object.

    :param name: the Notion table property name
    :param cls: the data type for the property (default = RichText)
    :param default: a default value when creating new objects
    """

    log.debug("creating new Property: %s", name)

    def getter(self):
        """Return the current value of the property as a python object."""

        # TODO return None if the property is empty (regardless of type)...

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        log.debug("getter %s [%s]", cls, name)

        try:
            prop = self.page[name]

        except AttributeError:
            log.debug("property '%s' does not exist in Page; returning default", name)
            return default

        if not isinstance(prop, cls):
            raise TypeError("Type mismatch")

        # convert native objects to expected types
        if isinstance(prop, NativeTypeMixin):
            return prop.Value

        return prop

    def setter(self, value):
        """Set the property to the given value."""

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        # TODO only set the value if it has changed from the existing
        log.debug("setter %s [%s] => %s %s", cls, name, value, type(value))

        # convert native objects to expected types
        if isinstance(value, cls):
            prop = value

        elif hasattr(cls, "from_value"):
            from_value = cls.from_value
            prop = from_value(value)

        else:
            raise ValueError(f"Value does not match expected type: {cls}")

        # update the local property
        self.page[name] = prop

        # update the property live on the server
        self._orm_session_.pages.update(self.page, **{name: prop})

        # TODO consider reloading things like last_edited_time and formulas

    return property(getter, setter)


def connected_page(session=None, cls=ConnectedPageBase):
    """Returns a base class for "connected" pages through the Notion API."""

    if not issubclass(cls, ConnectedPageBase):
        raise ValueError("cls must subclass ConnectedPageBase")

    class _ConnectedPage(cls):
        _orm_database_ = None
        _orm_database_id_ = None
        _orm_session_ = None
        _orm_late_bind_ = None

        def __init_subclass__(cls, database=None, **kwargs):
            """Attach the ConnectedPage to the given database ID."""
            super().__init_subclass__(**kwargs)

            if cls._orm_database_id_ is not None:
                raise TypeError("Object {cls} registered to: {database}")

            if database:
                cls._orm_database_id_ = database

            elif hasattr(cls, "__database__"):
                cls._orm_database_id_ = cls.__database__

            else:
                raise ValueError("Missing 'database' for ConnectedPage: {cls}")

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

            # XXX if we want to grab the Database on binding...
            # cls._orm_database_ = to_session.databases.retrieve(cls._orm_database_id_)

    return _ConnectedPage
