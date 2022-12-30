#!/usr/bin/env python3

"""This script demonstrates setting properties on a page manually.

The script accepts a single command line option, which is a page ID.  It will then
display information about the properties and update a few of them.

Note that this script assumes the database has already been created with required
fields.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional import types

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# get an existing page...
page = notion.pages.retrieve(page_id)
print(f"{page.Title} => {page.url}")

# print all current properties on the page...
for name, value in page.properties.items():

    # use the endpoint to retrive the full property data
    prop = notion.pages.properties.retrieve(page_id, value.id)

    print(f"{name} [{prop.id}] => {prop}")

# update a property on the page...
notion.pages.update(page, Complete=types.Checkbox[True])
