#!/usr/bin/env python3

"""This script demonstrates querying databases in Notional.

The script accepts a single command line option, which is a database ID.  It will then
query the database for all results and display some information.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import json
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)

import notional
from notional.query import PropertyFilter, TextFilter

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

## query for all values sorted by Title

sort = {"direction": "ascending", "property": "Title"}
query = notion.databases.query(dbid).sort(sort)

print("== All Results ==")
for data in query.execute():
    print(f"{data['id']} => {data['url']}")

## filter for specific values...

query = notion.databases.query(dbid).filter(
    PropertyFilter.where_text(contains="project")
)

data = query.first()
print("== First Result ==")
print(f"{json.dumps(data, indent=4)}")
