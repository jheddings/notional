#!/usr/bin/env python3

"""This script demonstrates interacting with Mention objects in Notional.

The script accepts a single command line option, which is a page ID.  It will then
add a mention object to that page for the current user.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys
from datetime import date, timedelta

from notional import user

logging.basicConfig(level=logging.INFO)

import notional
from notional import blocks, types

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# get an existing page...
page = notion.pages.retrieve(page_id)
print(f"{page.Title} => {page.url}")

# find the first user in the workspace
friend = None

for acct in notion.users.list():
    # we cannot mention bots, so find the first Person
    if isinstance(acct, user.Person):
        friend = acct
        break

# set up a mention for tomorrow
tomm = date.today() + timedelta(days=1)

print(f"Notifying {friend} for {tomm}")

para = blocks.Paragraph[
    types.MentionUser[friend],
    " please review ",
    types.MentionPage[page],
    " by ",
    types.MentionDate[tomm],
]

notion.blocks.children.append(page, para)
