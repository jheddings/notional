# notional #

<a href="https://pypi.org/project/notional"><img src="https://img.shields.io/pypi/v/notional.svg" alt="PyPI"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/jheddings/notional" alt="License"></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-black" alt="Code style"></a>

A high level interface and object model for the Notion SDK.  This is loosely modeled
after concepts found in [SQLAlchemy](http://www.sqlalchemy.org) and
[MongoEngine](http://mongoengine.org).  This module is built on the excellent
[notion-sdk-py](https://github.com/ramnes/notion-sdk-py) library, providing higher-
level access to the API.

> :warning: **Work In Progress**: The interfaces in this module are still in development
and are likely to change.  Furthermore, documentation is pretty sparse so use at your
own risk!

That being said, if you do use this library, please drop me a message!

## Installation ##

Install the most recent release using PyPi:


```shell
pip install notional
```

Or install the most recent code from the GitHub repo (this may be unstable!):

```shell
pip install git+https://github.com/jheddings/notional.git
```

*Note:* it is recommended to use a virtual environment (`venv`) for installing libraries
to prevent conflicting dependency versions.

## Usage ##

Connect to the API using an integration token or an OAuth access token:

```python
import notional

notion = notional.connect(auth=AUTH_TOKEN)

# do some things
```

### Token Security ###

It is generally a best practice to read the auth token from an environment variable or
a secrets file.  To prevent accidental exposure, it is NOT recommended to save the token
in source.  For more information, read about Notion authorization 
[here](https://developers.notion.com/docs/authorization).

## Iterators ##

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

## Query Builder ##

Notional provides a query builder for interating with the Notion API.  Query targets can
be either a specific database ID or a custom ORM type.

### Filters ###

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

### Sorting ###

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
[read the official documentation](https://developers.notion.com/reference/post-database-query).

## ORM ###

This library has support for defining custom data types that wrap Notion pages. Typically,
these pages are entries in a database (collection) with a consistent schema.

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

## Parsers ##

Notional includes several parsers for importing exernal content.  They will accept
either string (data) or file-like objects to provide the input content.

### HTML Parser ###

The HTML parser read an HTML document into Notion API objects.  From there, the caller
may create a page in Notion using the rendered content.

```python
from notional.parser import HtmlParser

parser = HtmlParser(base="https://www.example.com/")

with open(filename, "r") as fp:
    parser.parse(fp)

doc = notion.pages.create(
    parent=parent_page,
    title=parser.title,
    children=parser.content,
)
```

*Note:* while the parser aims to be general purpose, there may be conditions where it
cannot interpret the HTML document.  Please submit an issue if you find an example of
valid HTML that is not properly converted.

### CSV Parser ###

The CSV parser will read comma-separate value content and generate the appropriate 
database along with content.  In order to populate the database, the contents must
be created as individual pages.

```python
from notional.parser import CsvParser

parser = CsvParser(header_row=True)

with open(filename, "r") as fp:
    parser.parse(fp)

doc = notion.databases.create(
    parent=parent_page,
    title=parser.title,
    schema=parser.schema,
)

for props in parser.content:
    page = notion.pages.create(
        parent=db,
        properties=props,
    )
```

## Contributing ##

I built this module so that I could interact with Notion in a way that made sense to
me.  Hopefully, others will find it useful.  If someone is particularly passionate about
this area, I would be happy to consider other maintainers or contributors.

Any pull requests or other submissions are welcome.  As most open source projects go, this
is a side project.  Large submissions will take time to review for acceptance, so breaking
them into smaller pieces is always preferred.  Thanks in advance!

Formatted using `black` and `isort`, checked using `flake8`.

### Known Issues ###

See [Issues](https://github.com/jheddings/notional/issues) on github.

### Feature Requests ###

See [Issues](https://github.com/jheddings/notional/issues) on github.
