#!/usr/bin/env python3

import json
import logging
import os
import sys

import notional

logging.basicConfig(level=logging.INFO)

database_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

db = notion.database(database_id)

print(f"{db.Title}")
