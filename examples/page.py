#!/usr/bin/env python3

"""This script demonstrates interacting with Page objects in Notional.

The script accepts a single command line option, which is a page ID.  It will then
display information about the Page, as well as create a sub-page with content.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

import notional
from notional import blocks

logging.basicConfig(level=logging.INFO)

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# get an existing page...
page = notion.pages.retrieve(page_id)
print(f"{page.Title} => {page.url}")

# print all children blocks on this page...
for block in notion.blocks.children.list(page):
    print(f"{block.type} => {type(block)}")

# create a new page
page = notion.pages.create(parent=page, title="Hello World")
print(f"{page.Title} => {page.url}")

# add blocks to the page...
notion.blocks.children.append(
    page,
    blocks.Heading1.from_text("Welcome!"),
    blocks.Paragraph.from_text("Good to see you again!"),
)
