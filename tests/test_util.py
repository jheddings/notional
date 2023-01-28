"""Unit tests for Notional util methods."""

from uuid import UUID, uuid4

from notional import util


def test_notion_id_regex():
    """Make sure we can parse UUID's with and without dashes."""

    id = uuid4()

    short_uuid = id.hex
    m = util.uuid_re.match(short_uuid)

    assert m is not None
    assert UUID(m.string) == id

    long_uuid = str(id)
    m = util.uuid_re.match(long_uuid)

    assert m is not None
    assert UUID(m.string) == id
