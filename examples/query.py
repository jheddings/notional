#!/usr/bin/env python3

import os
import sys
import json
import notional

dbid = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)
sorts = [{"direction": "ascending", "property": "Last Update"}]

query = notion.query(dbid).sort(sorts)

data = query.first()
print("== First Result ==")
print(f"{json.dumps(data, indent=4)}")

print("== All Results ==")
for data in query.execute():
    print(f"{data['id']} => {data['url']}")
