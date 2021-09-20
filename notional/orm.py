"""Utilities for working with Notion as an ORM."""

import logging

from .records import DatabaseParent, Page
from .types import NativeTypeMixin, PropertyValue, RichText

log = logging.getLogger(__name__)


class ConnectedPageBase(object):
    """Base class for "live" pages via the Notion API."""

    def __init__(self, **data):
        self.page = Page(**data)

    @property
    def id(self):
        """Return the ID of this page (if available)."""

        return None if self.page is None else self.page.id

    @property
    def children(self):
        """Return an iterator for all child blocks of this Page."""

        return EndpointIterator(
            endpoint=self._session.blocks.children.list, block_id=self.id
        )

    def append(self, *blocks):
        """Append the given blocks as children of this ConnectedPage."""

        self._orm_session_.blocks.children.append(parent=self.page, *blocks)

    @classmethod
    def create(cls, **properties):
        """Creates a new instance of the ConnectedPage type."""

        log.debug(f"creating new {cls} :: {cls._orm_database_id_}")

        parent = DatabaseParent(database_id=cls._orm_database_id_)

        # TODO convert properties to a dict for create...
        # props = cls.kwargs_to_props(properties)
        props = dict()

        page = cls._orm_session_.pages.create(parent=parent, properties=props)

        return cls(**page.dict())

    @classmethod
    def kwargs_to_props(cls, **kwargs):
        """Converts the list of keyword args to a dict of properties."""

        props = dict()

        for name, prop in properties.items():
            if isinstance(prop, PropertyValue):
                props[name] = prop.to_api()

            elif isinstance(prop, dict):
                props[name] = prop

            elif hasattr(cls, name):
                field = getattr(cls, name)
                prop = field.from_value(prop)  # FIXME
                props[name] = prop.to_api()

            else:
                raise ValueError(f"Unsupported property: {name}")

        return props

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

    def fget(self):
        """Return the current value of the property as a python object."""

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        log.debug(f"fget {cls} [{name}]")

        try:
            prop = self.page[name]

        except AttributeError:
            log.debug(f"property '{name}' does not exist in Page; returning default")
            return default

        if not isinstance(prop, cls):
            raise TypeError(f"Type mismatch: expected '{cls}' but found '{type(prop)}'")

        # convert native objects to expected types
        if isinstance(prop, NativeTypeMixin):
            return prop.Value

        return prop

    def fset(self, value):
        """Set the property to the given value."""

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

        # TODO only set the value if it has changed from the existing
        log.debug(f"fset {cls} [{name}] => {value} {type(value)}")

        # convert from native objects to expected types
        if isinstance(value, cls):
            prop = value
        elif issubclass(cls, NativeTypeMixin):
            prop = cls.from_value(value)
        else:
            raise ValueError(f"Value does not match expected type: {cls}")

        # commit the changes directly to Notion
        props = {name: prop.to_api()}
        self._orm_session_.pages.update(self.page, properties=props)

    return property(fget, fset)


def connected_page(session=None, cls=ConnectedPageBase):
    """Returns a base class for "connected" pages through the Notion API."""

    if not issubclass(cls, ConnectedPageBase):
        raise ValueError("cls must subclass ConnectedPageBase")

    class _ConnectedPage(cls):
        _orm_session_ = None
        _orm_database_id_ = None

        def __init_subclass__(cls, database, **kwargs):
            """Attach the ConnectedPage to the given database ID."""
            super().__init_subclass__(**kwargs)

            if database is None:
                raise ValueError("Missing 'database' for ConnectedPage: {cls}")

            if cls._orm_database_id_ is not None:
                raise TypeError("Object {cls} registered to: {database}")

            cls._orm_database_id_ = database

            cls.bind(session)

            log.debug(f"registered connected page :: {cls} => {database}")

        @classmethod
        def bind(cls, session):
            """Attach this ConnectedPage to the given session.

            Setting this to None will detach the page.
            """

            cls._orm_session_ = session

    return _ConnectedPage
