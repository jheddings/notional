"""Unit tests for Notional util methods."""

from uuid import UUID, uuid4

from notional import util

BASE_URL = "https://www.notion.so"


def test_parse_notion_id():
    """Make sure we can parse UUID's with and without dashes."""

    id = uuid4()

    short_uuid = id.hex
    m = util.UUID_RE.match(short_uuid)

    assert m is not None
    assert UUID(m.string) == id

    long_uuid = str(id)
    m = util.UUID_RE.match(long_uuid)

    assert m is not None
    assert UUID(m.string) == id


def test_parse_page_url_id():
    """Make sure we can parse Notion page URLs."""

    page_id = uuid4()
    title = "My Page"

    # Short URL (no title)
    url = f"{BASE_URL}/{page_id}"
    exid = util.extract_id_from_string(url)

    assert exid is not None
    assert UUID(exid) == page_id

    # Long URL (with title)
    url = f"{BASE_URL}/{title}-{page_id}"
    exid = util.extract_id_from_string(url)

    assert exid is not None
    assert UUID(exid) == page_id


def test_parse_block_url_id():
    """Make sure we can parse Notion block URLs."""

    page_id = uuid4()
    block_id = uuid4()
    title = "Another-Page"
    username = "alice"

    url = f"{BASE_URL}/{username}/{title}-{page_id}#{block_id}"
    exid = util.extract_id_from_string(url)

    assert exid is not None
    assert UUID(exid) == block_id

    # sometimes, we seem to have data in the query string
    url = f"{BASE_URL}/{username}/{title}-{page_id}?pvs=4#{block_id}"
    exid = util.extract_id_from_string(url)

    assert exid is not None
    assert UUID(exid) == block_id
