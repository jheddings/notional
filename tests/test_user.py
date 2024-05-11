"""Unit tests for the Notional user objects."""

import pytest

from notional.session import Session
from notional.user import Bot, Person, User

ALICE = """{
  "type": "person",
  "object": "user",
  "id": "fb187a7b-547c-47b0-a575-8dc15b02138b",
  "name": "Alice",
  "avatar_url": "https://static.wikia.nocookie.net/disney/images/7/75/Profile_-_Alice.jpeg",
  "person": {
    "email": "nobody@null.com"
  }
}"""

STAN = """{
  "type": "bot",
  "object": "user",
  "id": "baa4465c-9760-4907-9939-4f080bb7ea43",
  "name": "Stanley",
  "avatar_url": null,
  "bot": {
    "owner": { "type": "workspace" },
    "workspace_name": "notional::test_user"
  }
}"""


def test_parse_alice():
    """Create a standard user from API data."""
    user = User.deserialize(ALICE)

    assert type(user) == Person
    assert user.name == "Alice"


def test_parse_stan():
    """Create a bot user from API data."""
    user = User.deserialize(STAN)

    assert type(user) == Bot
    assert user.name == "Stanley"
    assert user.avatar_url is None


@pytest.mark.vcr()
def test_user_list(notion: Session):
    """Confirm that we can list some users."""
    num_users = 0

    for orig in notion.users.list():
        dup = notion.users.retrieve(orig.id)
        assert orig == dup
        num_users += 1

    assert num_users > 0


@pytest.mark.vcr()
def test_me_bot(notion: Session):
    """Verify that the current user looks valid."""
    me = notion.users.me()

    assert me is not None
    assert isinstance(me, Bot)
