"""Utility methods for Notional."""

import re

_base_url_pattern = r"https://(www)?.notion.so/"
_uuid_pattern = r"[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}"

UUID_RE = re.compile(rf"^(?P<id>{_uuid_pattern})$")

PAGE_URL_RE = re.compile(
    rf"""^
      {_base_url_pattern}
      ((?P<username>.*)/)?
      ((?P<title>.+)-)?
      (?P<page_id>{_uuid_pattern})
    $""",
    flags=re.IGNORECASE | re.VERBOSE,
)

BLOCK_URL_RE = re.compile(
    rf"""^
      {_base_url_pattern}
      (?P<username>.*)/
      (?P<title>.+)-
      (?P<page_id>{_uuid_pattern})
      (\?(?P<query>.+))?
      \#(?P<block_id>{_uuid_pattern})
    $""",
    flags=re.IGNORECASE | re.VERBOSE,
)


def extract_id_from_string(string) -> str:
    """Examine the given string to find a valid Notion object ID."""

    m = UUID_RE.match(string)
    if m is not None:
        return m.group("id")

    m = PAGE_URL_RE.match(string)
    if m is not None:
        return m.group("page_id")

    m = BLOCK_URL_RE.match(string)
    if m is not None:
        return m.group("block_id")

    raise ValueError(f"invalid Notion ID string: {string}")
