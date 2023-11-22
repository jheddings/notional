#!/usr/bin/env python3

"""This script demonstrates importing documents into Notion.

The script accepts two command line arguments:
- The first is a page ID where the content will be imported.
- The second is the local document that will be imported.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import os
import sys

import notional
from notional.parser import CsvParser, HtmlParser

parent_id = sys.argv[1]
filename = sys.argv[2]

(basename, ext) = os.path.splitext(filename)

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)

print(f"Parsing document: {filename}...")

# get the existing parent page...
parent = notion.pages.retrieve(parent_id)

## PARSE HTML FILE ##

if ext == ".html" or ext == ".htm":
    parser = HtmlParser(base="https://www.example.com/")

    # parse the source content
    with open(filename) as fp:
        parser.parse(fp)

    # create the page and upload the parsed content
    doc = notion.pages.create(
        parent=parent,
        title=parser.title,
        children=parser.content,
    )

    print(f"{doc.Title} => {doc.url}")

## PARSE CSV FILE ##

elif ext == ".csv":
    parser = CsvParser(header_row=True, title_column=0)

    # parse the source content
    with open(filename) as fp:
        parser.parse(fp)

    # create the page and upload the parsed content
    db = notion.databases.create(
        parent=parent,
        title=parser.title,
        schema=parser.schema,
    )

    print(f"{db.Title} => {db.url}")

    for props in parser.content:
        page = notion.pages.create(
            parent=db,
            properties=props,
        )

        print(f":: {page.Title} => {page.url}")

else:
    print(f"Unrecognized file format: {filename}")
