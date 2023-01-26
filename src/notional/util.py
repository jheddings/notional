"""Utility methods for Notional."""

import re

_uuid_regex = r"[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}"

notion_id_re = re.compile(_uuid_regex)

page_url_short_re = re.compile(
    rf"""https://www.notion.so/
    (?P<page_id>{_uuid_regex})
    """,
    flags=re.IGNORECASE | re.X,
)

page_url_long_re = re.compile(
    rf"""https://www.notion.so/
    (?P<title>.*)-
    (?P<page_id>{_uuid_regex})
    """,
    flags=re.IGNORECASE | re.X,
)

block_url_long_re = re.compile(
    rf"""https://www.notion.so/
    (?P<username>.*)/
    (?P<title>.*)-
    (?P<page_id>{_uuid_regex})
    #(?P<block_id>{_uuid_regex})
    """,
    flags=re.IGNORECASE | re.X,
)


def extract_id_from_string(string):
    """Examine the given string to find a Notion object ID."""

    m = page_url_long_re.match(string)
    if m is not None:
        return m.group("page_id")

    m = page_url_short_re.match(string)
    if m is not None:
        return m.group("page_id")

    return string
