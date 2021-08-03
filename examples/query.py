#!/usr/bin/env python3

import sys
import os
import json
import notional

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)
sort = {"direction": "ascending", "property": "Last Update"}

query = notion.query(dbid).sort(sort)

data = query.first()
print("== First Result ==")
print(f"{json.dumps(data, indent=4)}")

print("== All Results ==")
for data in query.execute():
    print(f"{data['id']} => {data['url']}")
