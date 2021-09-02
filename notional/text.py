"""Utilities for working text, markdown & Rich Text in Notion."""

from enum import Enum

# this might be a place to capture other utilities for working with markdown, text
# rich text, etc...  the challenge is not importing types due to a circular ref.


def plain_text(*rtf):
    """Return the combined plain text from the list of RichText objects."""
    return "".join(text.plain_text for text in rtf)


class Color(str, Enum):
    """Basic color values."""

    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"


class FullColor(str, Enum):
    """Extended color values, including backgounds."""

    default = "default"
    gray = "gray"
    brown = "brown"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    blue = "blue"
    purple = "purple"
    pink = "pink"
    red = "red"

    gray_background = "gray_background"
    brown_background = "brown_background"
    orange_background = "orange_background"
    yellow_background = "yellow_background"
    green_background = "green_background"
    blue_background = "blue_background"
    purple_background = "purple_background"
    pink_background = "pink_background"
    red_background = "red_background"
