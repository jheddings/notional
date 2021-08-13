#!/usr/bin/env python3

import logging
import os
import sys

logging.basicConfig(level=logging.FATAL)

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
    DueDate = Property("Due Date", types.Date)
    Complete = Property("Complete", types.Checkbox)
    Reference = Property("Reference", types.Number)
    Status = Property("Status")


sort = {"direction": "ascending", "property": "Title"}

for task in notion.query(Task).sort(sort).execute():
    print(f"== {task.Title} ==")
    print(task.Status)

    task.Complete = False
    task.Priority = "High"

    task.commit()
