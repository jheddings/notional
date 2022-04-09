# Parsers #

Notional includes several parsers for importing exernal content.  They will accept
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
