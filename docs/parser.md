# Parsers #

Notional includes several parsers for importing external content. They will accept
either string (data) or file-like objects to provide the input content.

## HTML Parser ##

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

After parsing, the `HtmlParser` will contain `title`, `meta`, and `content`.

### `HtmlParser.title` ###

If the parser encounters a `<title>` element, this property will be set to the contents.

Otherwise, the parser will attempt to look for a `name` in the input data stream.
Typically, this would be the filename if the data is a file-like object.

If no `<title>` or `name` exists, this property will be `None`.

### `HtmlParser.meta` ###

The `meta` property is a `dict` containing data from `<meta>` tags in the input.  This
property is a `dict` where each element has the form `meta_name: meta_value`.

### `HtmlParser.content` ###

Content is rendered into a list of blocks, ready to be created or appended to a page.

## CSV Parser ##

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

The `CsvParser` accepts the follow configuration options when initialized:

- `header_row` - indicates that the input data has a header row, which will be used to
  generate the schema (defaults to `True`)
- `title_column` - indicates which column number to use as the title for entries
  (defaults to `0`)

After parsing, the `CsvParser` will contain `title`, `schema`, and `content`.

### `CsvParser.title` ###

The parser will attempt to read a `name` property from the input data source.  As seen
in the above example, this is a useful property when creating the database.

If there is no `name` available, this property will be `None`.

### `CsvParser.schema` ###

The parser will generate a schema for the CSV data, which is used when creating the
database.  The schema is presented as a `dict` where each element is the form
`field_name: field_type` and can be passed to the `databases.create()` method.

### `CsvParser.content` ###

CSV data is created as a list of page properties in the database.  The content must be
created as separate pages with the new database parent.  Specifically, the `content`
property is a `list` where each element is a `dict` of the form
`field_name: field_value`.  These elements are a full set of properties for creating a
new page.
