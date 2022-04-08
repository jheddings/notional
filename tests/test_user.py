import logging
import unittest

from notional.user import Bot, Person, User

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


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

BOB = """{
  "type": "bot",
  "object": "user",
  "id": "baa4465c-9760-4907-9939-4f080bb7ea43",
  "name": "Bob",
  "avatar_url": null,
  "bot": {}
}"""


class UserTest(unittest.TestCase):
    """Unit tests for the User API objects."""

    def test_parse_alice(self):
        """Create a standard user from API data."""
        user = User.parse_raw(ALICE)

        self.assertEqual(type(user), Person)
        self.assertEqual(user.name, "Alice")

    def test_parse_bob(self):
        """Create a bot user from API data."""
        user = User.parse_raw(BOB)

        self.assertEqual(type(user), Bot)
        self.assertEqual(user.name, "Bob")
        self.assertIsNone(user.avatar_url)
