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

import notional
from notional import blocks, types
from notional.orm import Property, connected_page

logging.basicConfig(level=logging.INFO)

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)
CustomPage = connected_page(notion)


class Task(CustomPage, database=sys.argv[1]):
    """Defines a custom Task data type."""

    Title = Property("Title", types.Title)
    Priority = Property("Priority", types.SelectOne)
    Tags = Property("Tags", types.MultiSelect)
    DueDate = Property("Due Date", types.Date)
    Complete = Property("Complete", types.Checkbox)
    Reference = Property("Reference", types.Number)
    LastUpdate = Property("Last Update", types.LastEditedTime)
    Status = Property("Status")


# display all tasks...  also, set a tag if it is not present (which requires commit)

sort = {"direction": "ascending", "property": "Title"}

for task in notion.query(Task).sort(sort).execute():
    print(f"== {task.Title} ==")
    print(task.Status)

    if "To Review" not in task.Tags:
        task.Tags += "To Review"

    task.commit()

# create a task...  properties can be set using keywords, according to their type

one_week = date.today() + timedelta(days=7)

# FIXME currently this does not work (the properties are not set)...

task = Task.create(
    Title="Hello World",
    Complete=False,
    Priority="High",
    Tags=["Draft"],
    DueDate=one_week,
)

print(f"{task.Title} @ {task.LastUpdate}")

# add task content...  append child blocks to this task

task.append(blocks.Paragraph.from_text("Welcome to the page!"))

task.commit()
