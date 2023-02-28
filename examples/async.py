"""This script demonstrates using an `AsyncSession` in Notional.

The script accepts a single command line option, which is a page ID.  It will then
display information about the Page, as well as create a sub-page with content.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import asyncio
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional


async def display_child_info(block, session):
    """Display information about children of a given block."""

    if not block.has_children:
        return

    for child in session.blocks.children.list(block):
        print(f"-- {child.type} => {type(child)} [{child.id}]")


async def display_page_info(page_id, session):
    """Display information about page."""

    # get an existing page...
    page = session.pages.retrieve(page_id)
    print(f"{page.Title} => {page.url}")

    # print all blocks on this page...
    for block in session.blocks.children.list(page):
        print(f"{block.type} => {type(block)} [{block.id}]")

        # ...and any children they might have
        await display_child_info(block)


async def main():
    """Perform the main action of the script."""

    page_id = sys.argv[1]
    auth_token = os.getenv("NOTION_AUTH_TOKEN")

    notion = notional.aconnect(auth=auth_token)
    await display_page_info(page_id, notion)


asyncio.run(main())
