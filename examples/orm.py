#!/usr/bin/env python3

import logging
import os
import sys

logging.basicConfig(level=logging.INFO)

import notional
from notional import types
from notional.orm import Property, connected_page

auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)
CustomPage = connected_page(notion)


class Task(CustomPage, database=sys.argv[1]):
    """Defines a Task data type for a Notion page."""

    Title = Property("Title", types.Title)
    Priority = Property("Priority", types.SelectOne)
    Tags = Property("Tags", types.MultiSelect)
    DueDate = Property("Due Date", types.Date)
    Complete = Property("Complete", types.Checkbox)
    Reference = Property("Reference", types.Number)
    LastUpdate = Property("Last Update", types.LastEditedTime)
    Status = Property("Status")


sort = {"direction": "ascending", "property": "Title"}

for task in notion.query(Task).sort(sort).execute():
    print(f"== {task.Title} ==")
    print(task.Status)

    if "To Review" not in task.Tags:
        task.Tags += "To Review"

    task.commit()

task = Task.create(
    Title="Hello World",
    Complete=False,
    Priority="High",
)

print(f"{task.Title} @ {task.LastUpdate}")
