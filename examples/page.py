#!/usr/bin/env python3

"""This script demonstrates interacting with Page objects in Notional.

The script accepts a single command line option, which is a page ID.  It will then
display information about the Page, as well as create a sub-page with content.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional import blocks, types

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# get an existing page...
page = notion.pages.retrieve(page_id)
print(f"{page.Title} => {page.url}")

# print all blocks on this page...
for block in notion.blocks.children.list(page):
    print(f"{block.type} => {type(block)} [{block.id}]")

    # ...and any children they might have
    if block.has_children:
        for child in notion.blocks.children.list(block):
            print(f"-- {child.type} => {type(child)} [{child.id}]")

# create a new page
welcome = blocks.Heading1.from_text("Welcome!")
new_page = notion.pages.create(parent=page, title="Hello World", children=[welcome])

print(f"{page.Title} => {page.url}")

# add more blocks to the page...
notion.blocks.children.append(
    new_page, blocks.Paragraph.from_text("Good to see you again!")
)

# change the page properties...
notion.pages.update(new_page, title=types.Title.from_value("Farewell"))

# archive (delete) the new page...
notion.pages.delete(new_page)
