# Quick Start #

Using Notional requires an understanding of concepts described in the
[Notion API](https://developers.notion.com/reference).  In particular, it is
important to understand authorization and the data model.

## Authorization ##

Obtain an [authentication token](https://developers.notion.com/docs/authorization)
from your Notion account.

### Token Security ###

It is generally a best practice to read the auth token from an environment variable or
a secrets file.  To prevent accidental exposure, it is NOT recommended to save the token
in source.

## Installation ##

Install the most recent release using PyPI:

```shell
pip install notional
```

*Note:* it is recommended to use a virtual environment (`venv`) for installing libraries
to prevent conflicting dependency versions.

## Connect ##

Connect to the API using an integration token or an OAuth access token:

```python
import notional

notion = notional.connect(auth=AUTH_TOKEN)
```

## Data Objects ##

The majority of the Notion API expresses capabilities through data objects that
follow a specific pattern.  It is good to be familiar with the Notion API representation
of these objects, as it will help understand concepts found in Notional.

Many common uses of data objects require interacting with the internal data. Notional
provides two helper methods for working with this structure: compose and call.

### Constructing ###

Constructing a data object requires manually setting up the internal data
structures.  Consider the following example:

```python
text = "It was a dark and stormy night..."
nested = TextObject.NestedData(content=text)
rtf = text.TextObject(text=nested, plain_text=text)
content = blocks.Paragraph.NestedData(text=[rtf])
para = blocks.Paragraph(paragraph=content)
```

Notice how we build the `NestedData` object in order to construct the final
`Paragraph`.  This approach provides the most versatility when building complex
objects.

Technical note: since Notional uses `pydantic` for object serialization under the
hood, the constructor for each object is generated based on the object properties.

### Composing ###

Composing a data object provides the caller a shorthand to construction.  Rather
than explicitly laying out the nested data, the `__compose__` method takes care of
setting up the internal data structure.

Consider our example from above.  Using the composable feature of a `Paragraph` block
changes the code like so:

```python
para = blocks.Paragraph["It was a dark and stormy night..."]
```

Note the use of `[ ]` in the composition example...  This instructs the `Paragraph`
to compose itself from the given parameters.  The acceptable parameters for this method
is specific to the object being composed.

Technical note: since the constructor is provided by `pydantic`, we do not override
it.  Instead, we have chosen to provide an alternate form of creating objects.  We
refer to this form as "composing" from basic types.

### Calling ###

Calling a data object provides access to the underlying data structure, which typically
contains the content of the object.

For example, to get the "checked" state of a `ToDo` block, we can use either the
nested data structure directly or call the block:

```python
todo = blocks.ToDo(...)

# direct access
checked = todo.to_do.checked

# nested data access
checked = todo().checked

# nested property access
checked = todo("checked")
```

In the above example, all three approaches for getting the `checked` field of our `ToDo`
block produce the same result.
