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
    "Cost": schema.Number[schema.NumberFormat.DOLLAR],
    "Supplier": schema.RichText(),
    "Inventory": schema.Number(),
}

parts_db = notion.databases.create(
    parent=page,
    title="Parts",
    schema=parts_schema,
)


class Part(CustomPage):
    """Defines a custom `Part` type in Notion."""

    __database__ = parts_db.id

    Name = orm.Property("Name", types.Title)
    Cost = orm.Property("Cost", types.Number)
    Inventory = orm.Property("Inventory", types.Number)
    Supplier = orm.Property("Supplier", types.RichText)


# create our product database...

product_schema = {
    "Name": schema.Title(),
    "Parts": schema.Relation[parts_db.id],
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


class Product(CustomPage):
    """Defines a custom `Product` type in Notion."""

    __database__ = product_db.id

    Name = orm.Property("Name", types.Title)
    Parts = orm.Property("Parts", types.Relation)
    COGS = orm.Property("COGS", types.Rollup)
    Quantity = orm.Property("Quantity", types.Number)


# add parts to the database...

x_throstle = Part.create(
    Name="X Throstle",
    Cost=25,
    Inventory=30,
    Supplier="Spacely Sprockets",
)

depthgrater = Part.create(
    Name="Depthgrater",
    Cost=1000,
    Inventory=5,
    Supplier="Knowhere",
)

quasipaddle = Part.create(
    Name="Quasipaddle",
    Cost=42,
    Inventory=37,
    Supplier="PRIVATE",
)

# now, build some products for the catalog...

capsule = Product.create(
    Name="Evacuation Capsule",
    Parts=types.Relation[[x_throstle, quasipaddle]],
    Quantity=3,
)

rocket = Product.create(
    Name="Rocket Ship",
    Parts=types.Relation[[x_throstle, depthgrater]],
    Quantity=1,
)

print(f"Capsule COGS: {capsule.COGS}")
