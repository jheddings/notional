# ORM #

This library has support for defining custom data types that wrap Notion pages.
Typically, these pages are entries in a database (collection) with a consistent schema.

```python
from notional import types
from notional.records import Page, Property

class Task(Page, database=NOTION_DATABASE_ID):
    Title = Property('Title', types.Title)
    Priority = Property('Priority', types.SelectOne)
    DueDate = Property('Due Date', types.Date)

for task in notion.databases.query(Task).execute():
    print(f"{task.Title} => {task.Priority}")
    task.DueDate = date.today()
    task.commit()
```

See the [examples](https://github.com/jheddings/notional/tree/main/examples) for more
information.
