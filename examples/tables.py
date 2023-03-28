#!/usr/bin/env python3

"""This script demonstrates interacting with Table blocks in Notional.

The script accepts a single command line option, which is a page ID.  It will then
create a table on the page and populate it with data.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

import notional
from notional import blocks

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

# get the existing page...
notion = notional.connect(auth=auth_token)
page = notion.pages.retrieve(page_id)

# compose the header row and initialize the table
header = blocks.TableRow["Date", "Amount", "Notes"]
table = blocks.Table[header]

timestamp = datetime.now()

for rownum in range(0, 10):
    row = blocks.TableRow[timestamp.isoformat(), str(rownum)]

    # all rows in a table must have the same width...  since we initialized the
    # table using a header with 3 cells, all rows must have 3 cells before appending

    if rownum % 2 == 0:
        row.append("even")
    else:
        row.append("odd")

    table.append(row)
    timestamp += timedelta(days=1)

# append the complete table to the target page
# NOTE that the table must contain valid content before adding to the page
notion.blocks.children.append(page, table)
