#!/usr/bin/env python3

"""This script demonstrates using iterators in Notional.

The script accepts a single command line option, which is a database ID.  It will then
use the query endpoint to display all records in the database.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

import notional
from notional.iterator import EndpointIterator

logging.basicConfig(level=logging.INFO)

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# NOTE calling the notional endpoint exposes the unerlying raw data endpoint

tasks = EndpointIterator(
    endpoint=notion.databases().query,
    database_id=dbid,
    sorts=[{"direction": "ascending", "property": "Last Update"}],
)

for data in tasks:
    print(f"{data['id']} => {data['url']}")
