# notional #

A simplified object model for the Notion SDK.

> :warning: **Work In Progress**: The interfaces in this module are still in development
and are likely to change frequently.  Furthermore, documentation is pretty sparse so use
at your own risk!

That being said, if you do use this library, please drop a message!  I'd love to see your
use case and how you are incorporating this into your project.

## Installation ##

Install using PyPi:

```
pip install notional

```

*Note:* it is recommended to use a virtual environment (`venv`) for installing libraries
to prevent conflicting dependency versions.

## Usage ###

Connect to the API using an integration token or an OAuth access token:

```python
import notional

notion = notional.connect(auth=AUTH_TOKEN)

# do some things

notion.commit()
```

## Iterators ###

The iterators provide convenient access to the Notion endpoints.  Rather than looking for
each page of data, the iterators take care of this and expose a standard Python iterator:

```python
import notional

from notional.iterator import EndpointIterator

notion = notional.connect(auth=AUTH_TOKEN)

tasks = EndpointIterator(
    endpoint=notion.databases.query,
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

## ORM ###

This library has support for defining custom data types that wrap Notion pages. Typically,
these pages are entries in a database (collection) with a consistent schema.

Currently, there is not a good way to iterate over custom data types.  This will be fixed
in a future release.

```python
from notional import types
from notional.records import Page, Property

class Task(Page):
    Title = Property('Title', types.Title)
    Priority = Property('Priority', types.SelectOne)
    DueDate = Property('Due Date', types.Date)

for data in tasks:
    task = Task(**data)
    print(f"{task.Title} => {task.Priority}")
    task.DueDate = date.today()
    task.commit()
```

See the examples for more information.

### Token Security ###

It is generally a best practice to read the auth token from an environment variable or
a secrets file.  To prevent accidental exposure, it is NOT recommended to save the token
in source.  For more information, read about Notion authorization here.

## Contributing ##

I built this module so that I could interact with Notion in a way that made sense to
me.  Hopefully, others will find it useful.  If someone is particularly passionate about
this area, I would be happy to consider other maintainers or contributors.

Any pull requests or other submissions are welcome.  As most open source projects go, this
is a side project.  Large submissions will take time to review for acceptance, so breaking
them into smaller pieces is always preferred.  Thanks in advance!

Formatted using `black`.

### Known Issues ###

See Issues on github.

### Feature Requests ###

See Issues on github.
