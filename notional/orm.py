"""Utilities for working with Notion as an ORM."""


def Attribute(name, cls=str, default=None):
    """Define a data attribute for a Notion Block.

    :param name: the attribute key in the Block
    :param cls: the data type for the property
    """

    log.debug("creating new Attribute: %s", name)

    def fget(self):
        """Return the current value of the attribute."""
        if not isinstance(self, Block):
            raise TypeError("Attributes must be used in a Block object")

        if self.__data__ is None:
            return None

        value = self.__data__.get(name, None)

        if value is None:
            return default

        # TODO support type conversion
        return value

    return property(fget)


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
        if not isinstance(self, Page):
            raise TypeError("Properties must be used in a Page object")

        data = self.get_property(name)
        if data is None:
            return default

        value = notion_to_python(data)

        if not isinstance(value, cls):
            raise TypeError(
                f"Type mismatch: expected '{cls}' but found '{type(value)}'"
            )

        # convert native objects to expected types
        if isinstance(value, NativePropertyValue):
            value = value.value

        return value

    def fset(self, value):
        """Set the property to the given value."""

        if not isinstance(self, Page):
            raise TypeError("Properties must be used in a Page object")

        # TODO only set the value if it has changed from the existing

        try:
            data = python_to_notion(value, cls)
        except TypeError:
            raise TypeError(
                f"Type mismatch: expected '{cls}' but found '{type(value)}'"
            )

        # to change the value of a property, we simply need to update the value in the
        # internal data structure...  future calls to fget will "do the right thing"

        self.set_property(name, data)

    return property(fget, fset)
