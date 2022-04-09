# Iterators #

The iterators provide convenient access to the Notion endpoints.  Rather than looking for
each page of data, the iterators take care of this and expose a standard Python iterator:

```python
import notional

from notional.iterator import EndpointIterator

notion = notional.connect(auth=AUTH_TOKEN)

tasks = EndpointIterator(
    endpoint=notion.databases().query,
    database_id=task_db_id,
    sorts=[
        {
            'direction': 'ascending',
            'property': 'Last Update'
        }
    ]
)

for data in tasks:
    # do the things
```

Note that the parameters to the iterator follow the standard API parameters for the
given endpoint.
