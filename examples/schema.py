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

notion = notional.connect(auth=auth_token, log_level=logging.DEBUG)

status = [
    schema.SelectOption(name="Backlog"),
    schema.SelectOption(name="Blocked", color="red"),
    schema.SelectOption(name="In Progress", color="yellow"),
    schema.SelectOption(name="Completed", color="green"),
]

# define our schema...
props = {
    "Name": schema.Title(),
    "Estimate": schema.Number.format("dollar"),
    "Approved": schema.Checkbox(),
    "Points": schema.Number(),
    "Due Date": schema.Date(),
    "Status": schema.Select.options(*status),
    "Last Update": schema.LastEditedTime(),
}

# get the existing page...
page = notion.pages.retrieve(page_id)

# create the database...
db = notion.databases.create(parent=page, title="Custom Database", schema=props)

# add an entry to the new database using from_ methods...

one_week = date.today() + timedelta(days=7)

entry = notion.pages.create(
    parent=db,
    properties={
        "Name": types.Title.from_value("Big Project"),
        "Approved": types.Checkbox.from_value(True),
        "Points": types.Number.from_value(42),
        "Status": types.SelectOne.from_value("In Progress"),
        "Due Date": types.Date.from_value(one_week),
        "Estimate": types.Number.from_value(1000000),
    },
)

# we can also construct complex values manually...

content = types.TextObject.NestedData(content="Small Project")
text = types.TextObject(plain_text=content.content, text=content)
name = types.Title(title=[text])

estimate = types.Number(number=12000)

approved = types.Checkbox(checkbox=False)

backlog = types.SelectValue(name="Backlog")
status = types.SelectOne(select=backlog)

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
