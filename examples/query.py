#!/usr/bin/env python3

"""This script demonstrates querying databases in Notional.

The script accepts a single command line option, which is a database ID.  It will then
query the database for all results and display some information.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)

import notional
from notional.query import SortDirection, TextConstraint

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

## query for all values sorted by Title

query = notion.databases.query(dbid).sort(
    property="Title", direction=SortDirection.ascending
)

print("== All Query Results ==")
for data in query.execute():
    print(f"{data.id} => {data.url}")

## filter for specific values...

query = (
    notion.databases.query(dbid)
    .filter(property="Title", text=TextConstraint(contains="project"))
    .limit(1)
)

data = query.first()
print("== First Query Result ==")
print(f"{data.json(indent=4)}")
