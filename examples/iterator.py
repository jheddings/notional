#!/usr/bin/env python3

"""This script demonstrates using iterators in Notional.

The script accepts a single command line option, which is a database ID.  It will then
use the query endpoint to display all records in the database.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional.iterator import EndpointIterator

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# NOTE iterators operate on the SDK endpoints... calling
# the notional endpoint exposes the notion_client endpoint

query = EndpointIterator(notion.databases().query)

params = {
    "database_id": dbid,
    "sorts": [
        {
            "direction": "ascending",
            "property": "Last Update",
        }
    ],
}

for data in query(**params):
    print(f"{data.id} [{data.object}] => {data.url}")
