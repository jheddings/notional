import json
import logging
import unittest
from datetime import date, datetime, timezone

from pydantic import ValidationError

from notional import types, user

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class TitlePropertyTest(unittest.TestCase):
    """Verify Title property values."""

    def test_ParseData(self):

        test_data = {
            "id": "title",
            "type": "title",
            "title": [
                {
                    "type": "text",
                    "text": {"content": "Buy milk", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "Buy milk",
                    "href": None,
                }
            ],
        }

        title = types.Title.parse_obj(test_data)

        self.assertEqual(title.id, "title")
        self.assertEqual(title.Value, "Buy milk")

    def test_FromValue(self):
        title = types.Title.from_value("Get more milk")
        self.assertEqual(title.Value, "Get more milk")


class NumberPropertyTest(unittest.TestCase):
    """Verify Number property values."""

    def test_ParseData(self):
        test_data = {"id": "XQOP", "type": "number", "number": 42}

        num = types.Number.parse_obj(test_data)

        self.assertEqual(num.type, "number")
        self.assertEqual(num.number, 42)

    def test_FromFloatValue(self):
        num = types.Number.from_value(2.718281828)
        self.assertEqual(num.Value, 2.718281828)

    def test_FromStringValue(self):
        num = types.Number.from_value("100.00")
        self.assertEqual(num.Value, 100)

    def test_FromBadString(self):
        with self.assertRaises(ValidationError):
            types.Number.from_value("twelve")


class CheckboxPropertyTest(unittest.TestCase):
    """Verify Checkbox property values."""

    def test_ParseData(self):
        test_data = {"id": "ax{O", "type": "checkbox", "checkbox": False}

        check = types.Checkbox.parse_obj(test_data)

        self.assertEqual(check.type, "checkbox")
        self.assertFalse(check.checkbox)

    def test_FromBooleanValue(self):
        check = types.Checkbox.from_value(True)
        self.assertTrue(check.Value)

    def test_FromStringValue(self):
        check = types.Checkbox.from_value("no")
        self.assertFalse(check.Value)

    def test_FromBadString(self):
        with self.assertRaises(ValidationError):
            types.Checkbox.from_value("foo")


class DatePropertyTest(unittest.TestCase):
    """Verify complex Date property values."""

    def test_ParseSingleDate(self):

        test_data = {
            "id": "[wke",
            "type": "date",
            "date": {"start": "2020-08-04", "end": None},
        }

        single = types.Date.parse_obj(test_data)

        self.assertEqual(single.type, "date")
        self.assertEqual(single.Start, date(2020, 8, 4))
        self.assertFalse(single.IsRange)

        with self.assertRaises(ValueError):
            if date(2020, 8, 4) in single:
                pass

    def test_ParseDateWithTime(self):

        test_data = {
            "id": "_mGp",
            "type": "date",
            "date": {"start": "2021-05-04T07:11:03.141Z", "end": None},
        }

        tstamp = types.Date.parse_obj(test_data)

        self.assertEqual(tstamp.type, "date")
        self.assertEqual(
            tstamp.Start, datetime(2021, 5, 4, 7, 11, 3, 141000, timezone.utc)
        )
        self.assertFalse(tstamp.IsRange)

    def test_ParseDateRange(self):
        test_data = {
            "id": "<|;g",
            "type": "date",
            "date": {"start": "1978-11-01", "end": "1978-11-30"},
        }

        span = types.Date.parse_obj(test_data)

        self.assertEqual(span.type, "date")
        self.assertTrue(span.IsRange)

        self.assertEqual(span.Start, date(1978, 11, 1))
        self.assertEqual(span.End, date(1978, 11, 30))

        self.assertIn(date(1978, 11, 18), span)
        self.assertIn(date(1978, 11, 1), span)
        self.assertIn(date(1978, 11, 30), span)


class SelectOnePropertyTest(unittest.TestCase):
    """Verify SelectOne property values."""

    def test_ParseData(self):

        test_data = {
            "id": "c::a",
            "type": "select",
            "select": {
                "id": "4e76c87f-2189-4560-88a7-95a5eca140dd",
                "name": "High",
                "color": "yellow",
            },
        }

        priority = types.SelectOne.parse_obj(test_data)

        self.assertEqual(priority.type, "select")
        self.assertEqual(priority, "High")
        self.assertEqual(priority.Value, "High")

    def test_FromValue(self):
        priority = types.SelectOne.from_value("URGENT")
        self.assertEqual(priority, "URGENT")


class MultiSelectPropertyTest(unittest.TestCase):
    """Verify MultiSelect property values."""

    def test_ParseData(self):

        test_data = {
            "id": "W:kr",
            "type": "multi_select",
            "multi_select": [
                {
                    "id": "89696e9c-17a8-4a90-b0a6-ede587d3705d",
                    "name": "Grocery",
                    "color": "default",
                }
            ],
        }

        tags = types.MultiSelect.parse_obj(test_data)

        self.assertEqual(tags.type, "multi_select")
        self.assertIn("Grocery", tags)

        tags += "TEMPORARY"
        self.assertIn("TEMPORARY", tags)

        tags -= "TEMPORARY"
        self.assertNotIn("TEMPORARY", tags)

    def test_FromValueArray(self):
        tags = types.MultiSelect.from_values("foo", None, "bar")
        self.assertListEqual(tags.Values, ["foo", "bar"])
        self.assertNotIn(None, tags)


class EmailPropertyTest(unittest.TestCase):
    """Verify Email property values."""

    def test_ParseData(self):
        test_data = {"id": "QU|p", "type": "email", "email": "alice@example.com"}

        contact = types.Email.parse_obj(test_data)

        self.assertEqual(contact.type, "email")
        self.assertEqual(contact.email, "alice@example.com")


class PhoneNumberPropertyTest(unittest.TestCase):
    """Verify PhoneNumber property values."""

    def test_ParseData(self):

        test_data = {
            "id": "tLo^",
            "type": "phone_number",
            "phone_number": "555-555-1234",
        }

        contact = types.PhoneNumber.parse_obj(test_data)

        self.assertEqual(contact.type, "phone_number")
        self.assertEqual(contact.phone_number, "555-555-1234")


class URLPropertyTest(unittest.TestCase):
    """Verify URL property values."""

    def test_ParseData(self):

        test_data = {
            "id": "rNKf",
            "type": "url",
            "url": "https://en.wikipedia.org/wiki/Milk",
        }

        wiki = types.URL.parse_obj(test_data)

        self.assertEqual(wiki.type, "url")
        self.assertEqual(wiki.url, "https://en.wikipedia.org/wiki/Milk")


class FormulaPropertyTest(unittest.TestCase):
    """Verify Formula property values."""

    def test_ParseStringFormula(self):

        test_data = {
            "id": "s|>T",
            "type": "formula",
            "formula": {"type": "string", "string": "Buy milk [Alice]"},
        }

        title = types.Formula.parse_obj(test_data)

        self.assertEqual(title.type, "formula")
        self.assertEqual(title.Result, "Buy milk [Alice]")

    def test_ParseIntFormula(self):

        test_data = {
            "id": "?Y=S",
            "type": "formula",
            "formula": {"type": "number", "number": 2020},
        }

        year = types.Formula.parse_obj(test_data)

        self.assertEqual(year.type, "formula")
        self.assertEqual(year.Result, 2020)

    def test_ParseDateFormula(self):

        test_data = {
            "id": "ab@]",
            "type": "formula",
            "formula": {"type": "date", "date": {"start": "2020-09-03", "end": None}},
        }

        up = types.Formula.parse_obj(test_data)
        real = types.DateRange(start=date(2020, 9, 3))

        self.assertEqual(up.type, "formula")
        self.assertEqual(up.Result, real)


class PeoplePropertyTest(unittest.TestCase):
    """Verify People property values."""

    def test_ParseData(self):

        test_data = {
            "id": "nQ<Y",
            "type": "people",
            "people": [
                {
                    "object": "user",
                    "id": "62e40b6e-3f05-494f-9220-d68a1995b54f",
                    "name": "Alice",
                    "avatar_url": None,
                    "type": "person",
                    "person": {"email": "alice@example.com"},
                }
            ],
        }

        owner = types.People.parse_obj(test_data)

        self.assertEqual(owner.type, "people")
        self.assertIn("Alice", owner)

        for person in owner:
            self.assertIsInstance(person, user.User)


class FilesPropertyTest(unittest.TestCase):
    """Verify Files property values."""

    def test_ParseData(self):

        test_data = {
            "id": "NNT{",
            "type": "files",
            "files": [
                {
                    "name": "glass.jpg",
                    "type": "external",
                    "external": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Glass_of_Milk_%2833657535532%29.jpg"
                    },
                }
            ],
        }

        files = types.Files.parse_obj(test_data)

        self.assertEqual(files.type, "files")
        self.assertIn("glass.jpg", files)


class CreatedPropertyTest(unittest.TestCase):
    def test_CreatedTime(self):
        """Verify CreatedTime property values."""

        test_data = {
            "id": "v}{N",
            "type": "created_time",
            "created_time": "1999-12-31T23:59:59.999Z",
        }

        created = types.CreatedTime.parse_obj(test_data)
        self.assertEqual(created.type, "created_time")

        self.assertEqual(
            created.created_time,
            datetime(1999, 12, 31, 23, 59, 59, 999000, timezone.utc),
        )

    def test_CreatedBy(self):
        """Verify CreatedBy property values."""

        test_data = {
            "id": "@yUe",
            "type": "created_by",
            "created_by": {
                "object": "user",
                "id": "65970102-79f4-48ed-8065-0ff257e46558",
                "name": "Bob the Person",
                "avatar_url": "https://upload.wikimedia.org/wikipedia/en/d/d0/Dogecoin_Logo.png",
                "type": "person",
                "person": {"email": "bob@example.com"},
            },
        }

        created = types.CreatedBy.parse_obj(test_data)
        self.assertEqual(created.type, "created_by")

        author = created.created_by
        self.assertEqual(author.name, "Bob the Person")


class LastEditedPropertyValueTest(unittest.TestCase):
    def test_LastEditedTime(self):
        """Verify LastEditedTime property values."""

        test_data = {
            "id": "HdA>",
            "type": "last_edited_time",
            "last_edited_time": "2000-01-01T00:00:00.000Z",
        }

        updated = types.LastEditedTime.parse_obj(test_data)
        self.assertEqual(updated.type, "last_edited_time")

        self.assertEqual(
            updated.last_edited_time,
            datetime(2000, 1, 1, 0, 0, 0, 0, timezone.utc),
        )

    def test_LastEditedBy(self):
        """Verify LastEditedBy property values."""

        test_data = {
            "id": "dxcT",
            "type": "last_edited_by",
            "last_edited_by": {
                "object": "user",
                "id": "62e40b6e-3f05-494f-9220-d68a1995b54f",
                "name": "Alice the Person",
                "avatar_url": None,
                "type": "person",
                "person": {"email": "alice@example.com"},
            },
        }

        updated = types.LastEditedBy.parse_obj(test_data)
        self.assertEqual(updated.type, "last_edited_by")

        author = updated.last_edited_by
        self.assertEqual(author.name, "Alice the Person")


class RichTextPropertyTest(unittest.TestCase):
    """Unit tests for the PropertyValue API objects."""

    def test_RichText(self):
        """Verify RichText property values."""

        rtf = types.RichText.parse_obj(self.test_data)
        self.assertEqual(rtf.type, "rich_text")
        self.assertEqual(rtf.Value, "Our milk is very old.")

        rtf = types.RichText.from_value("We have new milk.")
        self.assertEqual(rtf.Value, "We have new milk.")

    test_data = {
        "id": ":T<z",
        "type": "rich_text",
        "rich_text": [
            {
                "type": "text",
                "text": {"content": "Our milk is ", "link": None},
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "default",
                },
                "plain_text": "Our milk is ",
                "href": None,
            },
            {
                "type": "text",
                "text": {"content": "very", "link": None},
                "annotations": {
                    "bold": True,
                    "italic": False,
                    "strikethrough": False,
                    "underline": True,
                    "code": False,
                    "color": "default",
                },
                "plain_text": "very",
                "href": None,
            },
            {
                "type": "text",
                "text": {"content": " old", "link": None},
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": True,
                    "code": False,
                    "color": "default",
                },
                "plain_text": " old",
                "href": None,
            },
            {
                "type": "text",
                "text": {"content": ".", "link": None},
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "default",
                },
                "plain_text": ".",
                "href": None,
            },
        ],
    }
