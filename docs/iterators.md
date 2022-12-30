# Iterators #

The iterators provide convenient access to paginated data in the Notion API.

```python
import notional

from notional.iterator import EndpointIterator

notion = notional.connect(auth=NOTION_AUTH_TOKEN)

# be sure to use the notion_sdk endpoint for the iterator
query = EndpointIterator(notion.databases().query)

params = {
    database_id=task_db_id,
    sorts=[
        {
            'direction': 'ascending',
            'property': 'Last Update'
        }
    ]
}

for data in query(**params):
    # do the things
```

Note that the parameters to the iterator call use the standard API parameters for the
endpoint.
