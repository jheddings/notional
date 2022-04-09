# Query Builder #

Notional provides a query builder for interacting with the Notion API.  Query targets
can be either a specific database ID or a custom ORM type.

## Filters ##

Filters can be added for either timestamps or properties using the query builder.  They
operate using a set of constraints, depending on the object being filtered.  Constraints
may be appended to the query builder using keywords or by creating them directly:


```python
notion = notional.connect(auth=auth_token)

query = (
    notion.databases.query(dbid)
    .filter(property="Title", text=TextConstraint(contains="project"))
    .filter(LastEditedTimeFilter.create(DateConstraint(past_week={})))
    .limit(1)
)

data = query.first()

# process query result
```

## Sorting ##

Sorts can be added to the query using the `sort()` method:

```python
notion = notional.connect(auth=auth_token)

query = notion.databases.query(dbid).sort(
    property="Title", direction=SortDirection.ascending
)

for data in query.execute():
    # something magic happens
```

For more information about querying,
[read the official API documentation](https://developers.notion.com/reference/post-database-query).
