#!/usr/bin/env python3

"""This script demonstrates using the schema objects in Notion.

The script accepts a single command line option, which is a page ID.  It will then
create a database using a programmatic schema and add items.

Note that the schema is built using the `schema` imports where the page properties
are set using the `types` imports.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)

import notional
from notional import schema, types

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

# connect to Notion and load our top-level page
notion = notional.connect(auth=auth_token)
page = notion.pages.retrieve(page_id)

# define custom select options with colors to help organize
# we can also create options on the fly (which we will see later)

status = [
    schema.SelectOption(name="Backlog"),
    schema.SelectOption(name="Blocked", color="red"),
    schema.SelectOption(name="In Progress", color="yellow"),
    schema.SelectOption(name="Completed", color="green"),
]

# define our schema from Property Objects

props = {
    "Name": schema.Title(),
    "Estimate": schema.Number[schema.NumberFormat.DOLLAR],
    "Approved": schema.Checkbox(),
    "Points": schema.Number(),
    "Due Date": schema.Date(),
    "Status": schema.Select[status],
    "Last Update": schema.LastEditedTime(),
}

# create the database using our clever schema...
db = notion.databases.create(parent=page, title="Custom Database", schema=props)

# add an entry to the new database using from_ methods...

one_week = date.today() + timedelta(days=7)

entry = notion.pages.create(
    parent=db,
    properties={
        "Name": types.Title["Big Project"],
        "Approved": types.Checkbox[True],
        "Points": types.Number[42],
        "Status": types.SelectOne["In Progress"],
        "Due Date": types.Date[one_week],
        "Estimate": types.Number[1000000],
    },
)

# we can also construct complex values directly (rather than composing)...

content = types.TextObject._NestedData(content="Small Project")
text = types.TextObject(plain_text=content.content, text=content)
name = types.Title(title=[text])

estimate = types.Number(number=12000)

approved = types.Checkbox(checkbox=False)

# note that we can create new Select options on the fly...
canceled = types.SelectValue(name="Canceled")
status = types.SelectOne(select=canceled)

next_year = types.DateRange(
    start=date.today() + timedelta(days=365), end=date.today() + timedelta(days=2 * 365)
)

timeframe = types.Date(date=next_year)

entry = notion.pages.create(
    parent=db,
    properties={
        "Name": name,
        "Approved": approved,
        "Status": status,
        "Estimate": estimate,
        "Due Date": timeframe,
    },
)

# finally, cleanup our sample database...
notion.databases.delete(db)
