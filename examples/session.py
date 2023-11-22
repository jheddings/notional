#!/usr/bin/env python3

"""This script demonstrates working with the Session object.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import os

import notional

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)

notion.ping()
