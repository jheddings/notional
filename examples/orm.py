#!/usr/bin/env python3

import os
import sys
import notional
import logging

from notional import types
from notional.blocks import Page, Property

logging.basicConfig(level=logging.INFO)
auth_token = os.getenv("NOTION_AUTH_TOKEN")


class Task(Page):
    """Defines a Task data type for a Notion page."""

    __database__ = sys.argv[1]

    Title = Property("Title", types.Title)
    Priority = Property("Priority", types.SelectOne)
    DueDate = Property("Due Date", types.Date)
    Complete = Property("Complete", types.Checkbox)
    Status = Property("Status")


notion = notional.connect(auth=auth_token)
sort = {"direction": "ascending", "property": "Last Update"}

for task in notion.query(Task).sort(sort).execute():
    print(f"== {task.Title} ==")
    print(f"Priority: {task.Priority}")
    print(f"Due Date: {task.DueDate}")
    print(task.Status)

    task.Complete = False
    task.Priority = "High"
    task.commit()
