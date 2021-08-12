import json
import logging
import unittest
from datetime import date, datetime, timezone

from pydantic import BaseModel

from notional import types, user

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class PropertyValueTest(unittest.TestCase):
    """Unit tests for the PropertyValue API objects."""

    def setUp(self):
        self.props = json.loads(ALL_TYPE_DATA)

    # TODO a test to make sure all properties deserialize to correct types

    def test_Title(self):
        """Verify Title property values."""

        title = types.Title.parse_obj(self.props["Title"])

        self.assertEqual(title.id, "title")
        self.assertEqual(title.Value, "Buy milk")

        title.Value = "Get more milk"

        self.assertEqual(title.Value, "Get more milk")

    def test_RichText(self):
        """Verify RichText property values."""

        rtf = types.RichText.parse_obj(self.props["Status"])

        self.assertEqual(rtf.type, "rich_text")
        self.assertEqual(rtf.Value, "Our milk is very old.")

        rtf.Value = "We have new milk."

        self.assertEqual(rtf.Value, "We have new milk.")

    def test_Number(self):
        """Verify Number property values."""

        num = types.Number.parse_obj(self.props["Index"])

        self.assertEqual(num.type, "number")
        self.assertEqual(num.number, 42)

        num.Value = 86

        self.assertEqual(num.Value, 86)

    def test_Checkbox(self):
        """Verify Checkbox property values."""

        check = types.Checkbox.parse_obj(self.props["Complete"])

        self.assertEqual(check.type, "checkbox")
        self.assertFalse(check.checkbox)

        check.Value = True

        self.assertTrue(check.Value)

    def test_Date(self):
        """Verify complex Date property values."""

        single = types.Date.parse_obj(self.props["Due Date"])

        self.assertEqual(single.type, "date")
        self.assertEqual(single.Start, date(2020, 8, 4))
        self.assertFalse(single.IsRange)

        with self.assertRaises(ValueError):
            if date(2020, 8, 4) in single:
                pass

        tstamp = types.Date.parse_obj(self.props["Timestamp"])

        self.assertEqual(tstamp.type, "date")
        self.assertEqual(
            tstamp.Start, datetime(2021, 5, 4, 7, 11, 3, 141000, timezone.utc)
        )
        self.assertFalse(tstamp.IsRange)

        span = types.Date.parse_obj(self.props["Date Range"])

        self.assertEqual(span.type, "date")
        self.assertTrue(span.IsRange)

        self.assertEqual(span.Start, date(1978, 11, 1))
        self.assertEqual(span.End, date(1978, 11, 30))

        self.assertIn(date(1978, 11, 18), span)
        self.assertIn(date(1978, 11, 1), span)
        self.assertIn(date(1978, 11, 30), span)

    def test_Email(self):
        """Verify Email property values."""

        contact = types.Email.parse_obj(self.props["Contact Email"])

        self.assertEqual(contact.type, "email")
        self.assertEqual(contact.email, "alice@example.com")

    def test_PhoneNumber(self):
        """Verify PhoneNumber property values."""

        contact = types.PhoneNumber.parse_obj(self.props["Contact Phone"])

        self.assertEqual(contact.type, "phone_number")
        self.assertEqual(contact.phone_number, "555-555-1234")

    def test_URL(self):
        """Verify URL property values."""

        ref = types.URL.parse_obj(self.props["Reference"])

        self.assertEqual(ref.type, "url")
        self.assertEqual(ref.url, "https://en.wikipedia.org/wiki/Milk")

    def test_SelectOne(self):
        """Verify SelectOne property values."""

        priority = types.SelectOne.parse_obj(self.props["Priority"])

        self.assertEqual(priority.type, "select")
        self.assertEqual(priority, "High")
        self.assertEqual(priority.Value, "High")

    def test_MultiSelect(self):
        """Verify MultiSelect property values."""

        tags = types.MultiSelect.parse_obj(self.props["Tags"])

        self.assertEqual(tags.type, "multi_select")
        self.assertIn("Grocery", tags)

        tags += "TEMPORARY"

        self.assertIn("TEMPORARY", tags)

        tags -= "TEMPORARY"

        self.assertNotIn("TEMPORARY", tags)
        self.assertListEqual(tags.Values, ["Grocery"])

    def test_People(self):
        """Verify People property values."""

        owner = types.People.parse_obj(self.props["Owner"])

        self.assertEqual(owner.type, "people")
        self.assertIn("Alice", owner)

        for person in owner:
            self.assertIsInstance(person, user.User)

    def test_Files(self):
        """Verify Files property values."""

        files = types.Files.parse_obj(self.props["Attachments"])

        self.assertEqual(files.type, "files")
        self.assertIn("jug.jpeg", files)

    def test_Formula(self):
        """Verify Formula property values."""

        title = types.Formula.parse_obj(self.props["Full Title"])

        self.assertEqual(title.type, "formula")
        self.assertEqual(title.Result, "Buy milk [Alice]")

        year = types.Formula.parse_obj(self.props["Year"])

        self.assertEqual(year.type, "formula")
        self.assertEqual(year.Result, 2020)

        up = types.Formula.parse_obj(self.props["Next Time"])
        real = types.DateRange(start=date(2020, 9, 3))

        self.assertEqual(up.type, "formula")
        self.assertEqual(up.Result, real)

    def test_CreatedTime(self):
        """Verify CreatedTime property values."""

        created = types.CreatedTime.parse_obj(self.props["Created On"])

        self.assertEqual(created.type, "created_time")

        self.assertEqual(
            created.created_time,
            datetime(1999, 12, 31, 23, 59, 59, 999000, timezone.utc),
        )

    def test_CreatedBy(self):
        """Verify CreatedBy property values."""

        created = types.CreatedBy.parse_obj(self.props["Created By"])

        self.assertEqual(created.type, "created_by")

        creator = created.created_by

        self.assertEqual(creator.name, "Bob the Person")

    def test_LastEditedTime(self):
        """Verify LastEditedTime property values."""

        updated = types.LastEditedTime.parse_obj(self.props["Last Update"])

        self.assertEqual(updated.type, "last_edited_time")

        self.assertEqual(
            updated.last_edited_time,
            datetime(2000, 1, 1, 0, 0, 0, 0, timezone.utc),
        )

    def test_LastEditedBy(self):
        """Verify LastEditedBy property values."""

        updated = types.LastEditedBy.parse_obj(self.props["Updated By"])

        self.assertEqual(updated.type, "last_edited_by")

        updator = updated.last_edited_by

        self.assertEqual(updator.name, "Alice the Person")


ALL_TYPE_DATA = """{
  "Title": {
    "id": "title",
    "type": "title",
    "title": [
      {
        "type": "text",
        "text": {
          "content": "Buy milk",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "Buy milk",
        "href": null
      }
    ]
  },

  "Index": {
    "id": "XQOP",
    "type": "number",
    "number": 42
  },

  "Complete": {
    "id": "ax{O",
    "type": "checkbox",
    "checkbox": false
  },

  "Due Date": {
    "id": "[WkE",
    "type": "date",
    "date": {
      "start": "2020-08-04",
      "end": null
    }
  },

  "Timestamp": {
    "id": "_mGp",
    "type": "date",
    "date": {
      "start": "2021-05-04T07:11:03.141Z",
      "end": null
    }
  },

  "Date Range": {
    "id": "<|;g",
    "type": "date",
    "date": {
      "start": "1978-11-01",
      "end": "1978-11-30"
    }
  },

  "Priority": {
    "id": "c::a",
    "type": "select",
    "select": {
      "id": "4e76c87f-2189-4560-88a7-95a5eca140dd",
      "name": "High",
      "color": "yellow"
    }
  },

  "Tags": {
    "id": "W:kr",
    "type": "multi_select",
    "multi_select": [
      {
        "id": "89696e9c-17a8-4a90-b0a6-ede587d3705d",
        "name": "Grocery",
        "color": "default"
      }
    ]
  },

  "Reference": {
    "id": "rNKf",
    "type": "url",
    "url": "https://en.wikipedia.org/wiki/Milk"
  },

  "Contact Phone": {
    "id": "tLo^",
    "type": "phone_number",
    "phone_number": "555-555-1234"
  },

  "Contact Email": {
    "id": "QU|p",
    "type": "email",
    "email": "alice@example.com"
  },

  "Full Title": {
    "id": "s|>T",
    "type": "formula",
    "formula": {
      "type": "string",
      "string": "Buy milk [Alice]"
    }
  },

  "Year": {
    "id": "?Y=S",
    "type": "formula",
    "formula": {
      "type": "number",
      "number": 2020
    }
  },

  "Next Time": {
    "id": "ab@]",
    "type": "formula",
    "formula": {
      "type": "date",
      "date": {
        "start": "2020-09-03",
        "end": null
      }
    }
  },

  "Attachments": {
    "id": "NNT{",
    "type": "files",
    "files": [
      {
        "name": "glass.jpg"
      },
      {
        "name": "logo.png"
      },
      {
        "name": "jug.jpeg"
      }
    ]
  },

  "Owner": {
    "id": "nQ<Y",
    "type": "people",
    "people": [
      {
        "object": "user",
        "id": "62e40b6e-3f05-494f-9220-d68a1995b54f",
        "name": "Alice",
        "avatar_url": null,
        "type": "person",
        "person": {
          "email": "alice@example.com"
        }
      }
    ]
  },

  "Created On": {
    "id": "v}{N",
    "type": "created_time",
    "created_time": "1999-12-31T23:59:59.999Z"
  },

  "Created By": {
    "id": "@yUe",
    "type": "created_by",
    "created_by": {
      "object": "user",
      "id": "65970102-79f4-48ed-8065-0ff257e46558",
      "name": "Bob the Person",
      "avatar_url": "https://upload.wikimedia.org/wikipedia/en/d/d0/Dogecoin_Logo.png",
      "type": "person",
      "person": {
        "email": "bob@example.com"
      }
    }
  },

  "Last Update": {
    "id": "HdA>",
    "type": "last_edited_time",
    "last_edited_time": "2000-01-01T00:00:00.000Z"
  },

  "Updated By": {
    "id": "dxcT",
    "type": "last_edited_by",
    "last_edited_by": {
      "object": "user",
      "id": "62e40b6e-3f05-494f-9220-d68a1995b54f",
      "name": "Alice the Person",
      "avatar_url": null,
      "type": "person",
      "person": {
        "email": "alice@example.com"
      }
    }
  },

  "Status": {
    "id": ":T<z",
    "type": "rich_text",
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Our milk is ",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": "Our milk is ",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": "very",
          "link": null
        },
        "annotations": {
          "bold": true,
          "italic": false,
          "strikethrough": false,
          "underline": true,
          "code": false,
          "color": "default"
        },
        "plain_text": "very",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": " old",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": true,
          "code": false,
          "color": "default"
        },
        "plain_text": " old",
        "href": null
      },
      {
        "type": "text",
        "text": {
          "content": ".",
          "link": null
        },
        "annotations": {
          "bold": false,
          "italic": false,
          "strikethrough": false,
          "underline": false,
          "code": false,
          "color": "default"
        },
        "plain_text": ".",
        "href": null
      }
    ]
  }
}"""
