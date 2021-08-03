#!/usr/bin/env python3

import os
import sys
import notional

from notional import types
from notional.records import Page, Property

auth_token = os.getenv("NOTION_AUTH_TOKEN")


class Task(Page):
    """Defines a Task data type for a Notion page."""
    __database__ = sys.argv[1]

    Title = Property("Title", types.Title)
    Priority = Property("Priority", types.SelectOne)
    DueDate = Property("Due Date", types.Date)
    Complete = Property("Complete", types.Checkbox)


notion = notional.connect(auth=auth_token)
sort = {"direction": "ascending", "property": "Last Update"}

for task in notion.query(Task).sort(sort).execute():
    print(f"{task.Title} => {task.Priority}")

    task.Complete = True
    task.commit()
