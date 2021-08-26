#!/usr/bin/env python3

"""This script demonstrates using the schema objects in Notion.

The script accepts a single command line option, which is a page ID.  It will then
create a database using a programmatic schema and add items.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

import notional
from notional import schema

logging.basicConfig(level=logging.INFO)

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

status = [
    schema.SelectOption(name="Backlog"),
    schema.SelectOption(name="Blocked", color="red"),
    schema.SelectOption(name="In Progress", color="yellow"),
    schema.SelectOption(name="Completed", color="green"),
]

# FIXME currently this does not _fully_ work (nested data requires more work)...

# define our schema...
props = {
    "Name": schema.Title(),
    #    "Estimate": schema.Number([format="dollar"]),
    "Approved": schema.Checkbox(),
    "Points": schema.Number(),
    #    "Status": schema.Select([options=status]),
    "Last Update": schema.LastEditedTime(),
}

# get the existing page...
page = notion.pages.retrieve(page_id)

# create the database...
db = notion.databases.create(parent=page, title="Custom Database", schema=props)

# TODO add a few things to the new database...
# record = notion.create_page(parent=db, ...)
