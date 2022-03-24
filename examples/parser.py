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

logging.basicConfig(level=logging.INFO)

import notional
from notional.parser import HtmlDocumentParser

parent_id = sys.argv[1]
filename = sys.argv[2]

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)

print(f"Parsing document: {filename}...")

# get the existing parent page...
page = notion.pages.retrieve(parent_id)

# setup the parser, which is stateful (e.g. no concurrent use)
parser = HtmlDocumentParser(base="http://www.example.com/")

# parse the source content
with open(filename, "r") as fp:
    html = fp.read()

parser.parse(html)

# create the page and upload the parsed content
doc = notion.pages.create(
    parent=page,
    title=parser.title,
    children=parser.content,
)

print(f"{doc.Title} => {doc.url}")
