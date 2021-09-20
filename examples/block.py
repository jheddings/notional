#!/usr/bin/env python3

"""This script demonstrates interacting with Block objects in Notional.

The script accepts a single command line option, which is a block ID.  It will then
display information about the Block.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional import blocks

block_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

notion = notional.connect(auth=auth_token)

# get an existing page...
block = notion.blocks.retrieve(block_id)
print(block.json(indent=4))
