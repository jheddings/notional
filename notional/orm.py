"""Utilities for working with Notion as an ORM."""

import logging

from .blocks import Block, Page
from .types import NativeTypeMixin, RichText

log = logging.getLogger(__name__)


class ConnectedPageBase(object):
    def __init__(self, **data):
        self._pending_props_ = dict()
        self._pending_children_ = list()

        self.page = Page(**data)

    @classmethod
    def create(cls, **properties):
        """Creates a new instance of the ConnectedPage type."""
        # TODO add support for properties...

        log.debug(f"creating new {cls} :: {cls._orm_database_id_}")

        parent_id = {"database_id": cls._orm_database_id_}

        # TODO convert properties to a dict for create...
        props = { }
        #name: prop.dict(exclude_none=True) for name, prop in properties.items()

        data = cls._orm_session_.pages.create(parent=parent_id, properties=props)

        return cls(**data)

    def commit(self):
        """Commit any pending changes to this ConnectedPageBase."""

        num_changes = len(self._pending_props_) + len(self._pending_children_)

        if num_changes == 0:
            log.debug("no pending changes for page %s; nothing to do", num_changes)
            return

        page_id = self.page.id
        log.info("Committing %d changes to page %s...", num_changes, page_id)

        if len(self._pending_props_) > 0:
            log.debug(
                "=> committing %d properties :: %s",
                len(self._pending_props_),
                self._pending_props_,
            )
            self._orm_session_.pages.update(page_id, properties=self._pending_props_)
            self._pending_props_.clear()

        if len(self._pending_children_) > 0:
            log.debug(
                "=> committing %d children :: %s",
                len(self._pending_children_),
                self._pending_children_,
            )
            self._orm_session_.blocks.children.append(
                block_id=page_id, children=self._pending_children_
            )
            self._pending_children_.clear()


def Property(name, cls=RichText, default=None):
    """Define a property for a Notion Page object.

    These must be stored in the 'properties' attribute of the Notion data.

    :param name: the Notion table property name
    :param cls: the data type for the property (default = RichText)
    :param default: a default value when creating new objects
    """

    log.debug("creating new Property: %s", name)

    def fget(self):
        """Return the current value of the property as a python object."""

        if not isinstance(self, ConnectedPageBase):
            raise TypeError("Properties must be used in a ConnectedPage object")

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
        log.debug(f"set {cls} [{name}] => {value} {type(value)}")

        # convert from native objects to expected types
        if isinstance(value, cls):
            prop = value
        elif issubclass(cls, NativeTypeMixin):
            prop = cls.from_value(value)
        else:
            raise ValueError(f"Value does not match expected type: {cls}")

        self.page[name] = prop

        # add the object data to pending props for commit...
        self._pending_props_[name] = prop.dict(exclude_none=True)

    return property(fget, fset)


def connected_page(session, bind=ConnectedPageBase):
    """Returns a base class for "connected" pages through the Notion API."""

    if not issubclass(bind, ConnectedPageBase):
        raise ValueError("bind class must subclass ConnectedPageBase")

    class _ConnectedPage(bind):
        _orm_session_ = None
        _orm_database_id_ = None

        def __init_subclass__(cls, database, **kwargs):
            super().__init_subclass__(**kwargs)

            if database is None:
                raise ValueError("Missing 'database' for ConnectedPage: {cls}")

            if cls._orm_database_id_ is not None:
                raise TypeError("Object {cls} registered to: {database}")

            cls._orm_session_ = session
            cls._orm_database_id_ = database

            log.debug(f"registered connected page :: {cls} => {database}")

    return _ConnectedPage
