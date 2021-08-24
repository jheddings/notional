#!/usr/bin/env python3

"""This script demonstrates basic database interaction in Notional.

The script accepts a single command line option, which is a database ID.  It will then
retrieve the Database and display the schema.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

import notional

logging.basicConfig(level=logging.INFO)

database_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

db = notion.get_database(database_id)

print(f"== {db.Title} ==")

for name, prop in db.properties.items():
    print(f"{name} => {prop.type}")
