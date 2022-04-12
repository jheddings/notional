#!/usr/bin/env python3

"""This script demonstrates relationships between databases in Notion.

The script accepts a single command line option, which is a page ID.  It will then
create two databases using related fields.

The caller must set `NOTION_AUTH_TOKEN` to a valid integration token.
"""

import logging
import os
import sys

from notional import orm
from notional.orm import connected_page

logging.basicConfig(level=logging.INFO)

import notional
from notional import schema, types

page_id = sys.argv[1]
auth_token = os.getenv("NOTION_AUTH_TOKEN")

# connect to Notion and load our top-level page
notion = notional.connect(auth=auth_token)
page = notion.pages.retrieve(page_id)
CustomPage = connected_page(session=notion)

# create our parts database...

parts_schema = {
    "Name": schema.Title(),
    "Cost": schema.Number.format(schema.NumberFormat.DOLLAR),
    "Supplier": schema.RichText(),
    "Inventory": schema.Number(),
}

parts_db = notion.databases.create(parent=page, title="Parts", schema=parts_schema)

x_throstle = notion.pages.create(
    parent=parts_db,
    properties={
        "Name": types.Title.from_value("X Throstle"),
        "Cost": types.Number.from_value(25),
        "Inventory": types.Number.from_value(30),
        "Supplier": types.RichText.from_value("Spacely Sprockets"),
    },
)

depthgrater = notion.pages.create(
    parent=parts_db,
    properties={
        "Name": types.Title.from_value("Depthgrater"),
        "Cost": types.Number.from_value(1000),
        "Inventory": types.Number.from_value(5),
        "Supplier": types.RichText.from_value("Knowhere"),
    },
)

quasipaddle = notion.pages.create(
    parent=parts_db,
    properties={
        "Name": types.Title.from_value("Quasipaddle"),
        "Cost": types.Number.from_value(42),
        "Inventory": types.Number.from_value(37),
        "Supplier": types.RichText.from_value("PRIVATE"),
    },
)

# create our product database...

# XXX this could be cleaner with helper methods for Rollup

product_schema = {
    "Name": schema.Title(),
    "Parts": schema.Relation.database(parts_db.id),
    "COGS": schema.Rollup(
        rollup=schema.Rollup._NestedData(
            relation_property_name="Parts",
            rollup_property_name="Cost",
            function=schema.Function.SUM,
        ),
    ),
    "Quantity": schema.Number(),
}

product_db = notion.databases.create(
    parent=page,
    title="Products",
    schema=product_schema,
)

rocket = notion.pages.create(
    parent=product_db,
    properties={
        "Name": types.Title.from_value("Rocket Ship"),
        "Parts": types.Relation.pages(x_throstle, quasipaddle),
        "Quantity": types.Number.from_value(1),
    },
)

# we can also define these using ORM, which requires an existing database...


class Part(CustomPage):
    """Defines a custom `Part` type in Notion."""

    __database__ = parts_db.id

    Name = orm.Property("Name", types.Title)
    Cost = orm.Property("Cost", types.Number)
    Inventory = orm.Property("Inventory", types.Number)
    Supplier = orm.Property("Supplier", types.RichText)


class Product(CustomPage):
    """Defines a custom `Product` type in Notion."""

    __database__ = product_db.id

    Name = orm.Property("Name", types.Title)
    Parts = orm.Property("Parts", types.Relation)
    COGS = orm.Property("COGS", types.Rollup)
    Quantity = orm.Property("Quantity", types.Number)


capsule = Product.create(
    Name="Hello World",
    Parts=types.Relation.pages(x_throstle, depthgrater),
    Quantity=3,
)

print(f"Capsule COGS: {capsule.COGS}")
