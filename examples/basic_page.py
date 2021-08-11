#!/usr/bin/env python3

import json
import logging
import os
import sys

import notional

logging.basicConfig(level=logging.DEBUG)

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

page = notion.page(page_id)

# print(f"{page.Title} => {page.url}")

print(page.parent)
