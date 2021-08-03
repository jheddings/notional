#!/usr/bin/env python3

import os
import sys
import notional

from notional import types
from notional.records import Page, Property


class Task(Page):
    """Defines a Task data type for a Notion page."""

    Title = Property("Title", types.Title)
    Priority = Property("Priority", types.SelectOne)
    DueDate = Property("Due Date", types.Date)
    Complete = Property("Complete", types.Checkbox)


page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

session = notional.connect(auth=auth_token)
data = session.pages.retrieve(page_id)
task = Task(session, **data)

print(f"{task.Title} => {task.Priority}")

task.Complete = True
task.commit()
