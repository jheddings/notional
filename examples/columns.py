#!/usr/bin/env python3

"""This script demonstrates interacting with Column blockss in Notional.

The script accepts a single command line option, which is a page ID.  It will then
create a column list on the page with two columns containing blocks.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import os
import sys

import notional
from notional import blocks

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

# get the existing page...
notion = notional.connect(auth=auth_token)
page = notion.pages.retrieve(page_id)

# compose the columns from other blocks
left = blocks.Column[blocks.Paragraph["Hello"]]
right = blocks.Column[blocks.Paragraph["World"]]

# compose the column list
columns = blocks.ColumnList[left, right]

# append the complete list to the target page
# NOTE that the column list must contain valid content before adding to the page
notion.blocks.children.append(page, columns)
