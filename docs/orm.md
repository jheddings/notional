# Object-Relational Mapping #

This library has support for defining custom data types that wrap Notion pages.
Typically, these pages are entries in a database (collection) with a consistent schema.

## Custom Types ##

Custom types must exted the `ConnectedPage` object.  To do so, first initalize a session
and generate the page object:

```python
auth_token = os.getenv("NOTION_AUTH_TOKEN")
notion = notional.connect(auth=auth_token)
CustomPage = connected_page(session=notion)
```

## Data Objects ##

Users may define custom types that map to entries in a Notion database.  To accomplish
this, delcare a class and its members using Notional types:

```python
class Task(CustomPage, database=NOTION_DATABASE_ID):
    Title = Property('Title', schema.Title())
    Priority = Property('Priority', schema.SelectOne())
    DueDate = Property('Due Date', schema.Date())
```

Alternatively, you may set the database ID as a private member of the custom type:

```python
class Task(CustomPage):
    __database__ = NOTION_DATABSE_ID
```

In the examples, `NOTION_DATABASE_ID` is defined as a string or UUID of a database
visible to the current integration.

Review the [`schema`](reference/schema.md) reference for all available types.

## Querying ##

Use the `QueryBuilder` class to iterate over custom types:

```python
for task in notion.databases.query(Task).execute():
    print(f"{task.Title} => {task.Priority}")
    task.DueDate = date.today()
```

See the [examples](https://github.com/jheddings/notional/tree/main/examples) for more
information and additional usage.
