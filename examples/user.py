#!/usr/bin/env python3

import logging
import os
import sys

import notional
from notional.iterator import EndpointIterator
from notional.user import User

logging.basicConfig(level=logging.INFO)

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)

users = EndpointIterator(endpoint=notion.users.list)

for user_data in users:
    user = User.from_json(user_data)
    print(f"{user.name} => {user.type}")
