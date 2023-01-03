#!/usr/bin/env python3

"""This script demonstrates querying databases in Notional.

The script accepts a single command line option, which is a database ID.  It will then
query the database for all results and display some information.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional.query import (
    DateCondition,
    LastEditedTimeFilter,
    NumberCondition,
    SortDirection,
    TextCondition,
)

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

## query for all values sorted by Title

query = notion.databases.query(dbid).sort(
    property="Title", direction=SortDirection.ASCENDING
)

print("== All Query Results ==")
for data in query.execute():
    print(f"{data.id} => {data.url}")

## filter for specific values...

query = (
    notion.databases.query(dbid)
    .filter(property="Title", rich_text=TextCondition(contains="project"))
    .filter(property="Cost", number=NumberCondition(greater_than=1000000))
    .filter(LastEditedTimeFilter[DateCondition(past_week={})])
    .limit(1)
)

data = query.first()

if data:
    print("== First Query Result ==")
    print(f"{data.json(indent=4)}")
else:
    print("== Empty Result Set ==")
