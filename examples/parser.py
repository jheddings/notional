#!/usr/bin/env python3

"""This script demonstrates importing an HTML document into Notion.

The script accepts two command line arguments:
- The first is a page ID where the content will be imported.
- The second is a local HTML document that will be imported (using dormouse.html
as the example).

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)

import notional
from notional import parser

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# get an existing page...
page = notion.pages.retrieve(page_id)
print(f"{page.Title} => {page.url}")

with open(sys.argv[2], "r") as fp:
    html = fp.read()

doc = notion.pages.create(parent=page)
parser.HtmlDocumentParser(notion, doc).parse(html)
