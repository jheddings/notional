#!/usr/bin/env python3

"""This script demonstrates basic search features in Notional.

The script will search for a specified string, provided as a single argument.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional.query import SortDirection, TimestampKind

text = sys.argv[1]
db_only = True if len(sys.argv) > 2 and sys.argv[2] == "--db-only" else False

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)

query = notion.search(text).sort(
    timestamp=TimestampKind.LAST_EDITED_TIME, direction=SortDirection.ASCENDING
)

if db_only:
    query = query.filter(property="object", value="database")

data = query.first()

if data is None:
    print("No results found")
    sys.exit(1)

print("== First Result ==")
print(f"{data.json(indent=4)}")

print("== Remaining Results ==")
for result in query.execute():
    print(f"{result.id} => {result.url}")
