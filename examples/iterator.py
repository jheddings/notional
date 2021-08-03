#!/usr/bin/env python3

import os
import sys
import notional

from notional.iterator import EndpointIterator

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

session = notional.connect(auth=auth_token)

tasks = EndpointIterator(
    endpoint=session.databases.query,
    database_id=dbid,
    sorts=[{"direction": "ascending", "property": "Last Update"}],
)

for data in tasks:
    print(f"{data['id']} => {data['url']}")
