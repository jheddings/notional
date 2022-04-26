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
from notional import blocks, schema, types
from notional.orm import Property, connected_page
from notional.query import SortDirection

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)
CustomPage = connected_page(session=notion)


class Task(CustomPage):
    """Defines a custom Task data type."""

    __database__ = sys.argv[1]

    Title = Property("Title", schema.Title())
    Priority = Property("Priority", schema.Select())
    Tags = Property("Tags", schema.MultiSelect())
    Complete = Property("Complete", schema.Checkbox())
    DueDate = Property("Due Date", schema.Date())
    Attachments = Property("Attachments", schema.Files())
    Reference = Property("Reference", schema.Number())
    LastUpdate = Property("Last Update", schema.LastEditedTime())
    Status = Property("Status")


# display all tasks...  also, set a tag if it is not present

query = Task.query().sort(property="Title", direction=SortDirection.ASCENDING)

for task in query.execute():
    print(f"== {task.Title} ==")
    print(f"{task.Status} => {task.DueDate}")

    if "To Review" not in task.Tags:
        task.Tags += "To Review"

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

task.Attachments += types.ExternalFile[
    "https://miro.medium.com/max/2872/1*T-qHsJ6L5UjpJP-6JVZz0w.jpeg", "spoon.jpeg"
]

# add task content as child blocks of this task...
task += blocks.Paragraph["Welcome to the matrix."]

# alternative form to append multiple blocks in a single call...
task.append(blocks.Divider(), blocks.Quote["There is no spoon."])
