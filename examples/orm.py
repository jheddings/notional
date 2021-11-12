#!/usr/bin/env python3

"""This script demonstrates using the ORM helpers in Notional.

The script accepts a single command line option, which is a database ID.  It will then
define a custom class called `Task` for that database with required fields.

This script demonstrates how to query using custom types, as well as making changes
to database pages.  Finally, it will create a new `Task` object in the database.

Note that this script assumes the database has already been created with required
fields.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)

import notional
from notional import blocks, types
from notional.orm import Property, connected_page
from notional.query import SortDirection

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)
CustomPage = connected_page(session=notion)


class Task(CustomPage, database=sys.argv[1]):
    """Defines a custom Task data type."""

    Title = Property("Title", types.Title)
    Priority = Property("Priority", types.SelectOne)
    Tags = Property("Tags", types.MultiSelect)
    Complete = Property("Complete", types.Checkbox)
    DueDate = Property("Due Date", types.Date)
    Attachments = Property("Attachments", types.Files)
    Reference = Property("Reference", types.Number)
    LastUpdate = Property("Last Update", types.LastEditedTime)
    Status = Property("Status")


# display all tasks...  also, set a tag if it is not present

query = notion.databases.query(Task).sort(
    property="Title", direction=SortDirection.ascending
)

for task in query.execute():
    print(f"== {task.Title} ==")
    print(f"{task.Status} => {task.DueDate}")

    if "To Review" not in task.Tags:
        task.Tags += "To Review"

    task.commit()

# create a task...  properties can be set using keywords, according to their type

one_week = date.today() + timedelta(days=7)

task = Task.create(
    Title="Hello World",
    Complete=False,
    Priority="High",
    Tags=["Draft"],
    DueDate=one_week,
)

print(f"{task.Title} @ {task.LastUpdate}")

task.Attachments.append_url(
    "https://miro.medium.com/max/2872/1*T-qHsJ6L5UjpJP-6JVZz0w.jpeg"
)

# add task content as child blocks of this task...
task += blocks.Paragraph.from_text("Welcome to the matrix.")

# alternative form to append multiple blocks in a single call...
# task.append(blocks.Divider(), blocks.Quote.from_text("There is no spoon."))

task.commit()
