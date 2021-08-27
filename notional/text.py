"""Utilities for working text, markdown & Rich Text in Notion."""

# this might be a place to capture other utilities for working with markdown, text
# rich text, etc...  the challenge is not importing types due to a circular ref.

def plain_text(*rtf):
    """Return the combined plain text from the list of RichText objects."""
    return "".join(text.plain_text for text in rtf)
