"""Unit tests for the Notional session."""

import pytest

from notional.blocks import DataRecord
from notional.session import Session


@pytest.mark.vcr()
def test_active_session(notion: Session):
    """Verify the session reports as active."""
    assert notion.IsActive

    notion.close()
    assert not notion.IsActive


@pytest.mark.vcr()
def test_ping_session(notion: Session):
    """Verify the active session responds to a ping."""
    assert notion.ping()


@pytest.mark.vcr()
def test_simple_search(notion: Session):
    """Make sure search returns some results."""

    search = notion.search()

    num_results = 0

    for result in search.execute():
        assert isinstance(result, DataRecord)
        num_results += 1

    # sanity check to make sure some results came back
    assert num_results > 0
