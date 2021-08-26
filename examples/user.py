#!/usr/bin/env python3

"""This script demonstrates interacting with User objects in Notional.

The script will report information all for users found in the current workspace.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os

import notional
from notional.iterator import EndpointIterator
from notional.user import User

logging.basicConfig(level=logging.INFO)

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)

for user in notion.users.list():
    print(f"{user.name} => {user.type} :: {type(user)}")
