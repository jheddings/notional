#!/usr/bin/env python3

"""This script demonstrates basic search features in Notional.

The script will search for a specified string, provided as a single argument.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import json
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional.query import SortDirection, TimestampKind

text = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

query = notion.search(text).sort(
    timestamp=TimestampKind.LAST_EDITED_TIME, direction=SortDirection.ASCENDING
)

data = query.first()
print("== First Result ==")
print(f"{json.dumps(data, indent=4)}")

print("== Remaining Results ==")
for result in query.execute():
    print(f"{result['id']} => {result['url']}")
