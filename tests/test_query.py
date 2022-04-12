"""Unit tests for Notional query objects."""

import logging
import unittest

from notional import query

from .mocks import MockDataObject, mock_endpoint

# NOTE these tests help to debug issues in the query builder, however they do not
# perform an actual query.  the intent of these objects is to represent the API
# definition of the query, as opposed to run actual filter, sort, etc operations

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class QueryBuilderTests(unittest.TestCase):
    """Unit tests for the Query Builder class."""

    def test_empty_query(self):
        """Create an empty query."""
        qb = query.QueryBuilder(None)
        with self.assertRaises(ValueError):
            qb.first()

    def test_basic_number_constraint(self):
        """Filter a query based on a number value."""
        mock = mock_endpoint(1000, 100)

        qb = (
            query.QueryBuilder(mock, cls=MockDataObject)
            .filter(property="index", number=query.NumberConstraint(equals=42))
            .limit(1)
        )

        qb.first()

    def test_number_range_constraint(self):
        """Filter a query based on a number range."""
        mock = mock_endpoint(1000, 23)

        qb = (
            query.QueryBuilder(mock, cls=MockDataObject)
            .filter(
                property="index",
                number=query.NumberConstraint(greater_than=25),
            )
            .filter(
                property="index",
                number=query.NumberConstraint(less_than_or_equal_to=75),
            )
        )

        qb.first()

    def test_invalid_filter(self):
        """Make sure that bad filters give an error."""

        with self.assertRaises(ValueError):
            query.QueryBuilder(None).filter(bad_filter_name="INVALID")

    def test_invalid_sort(self):
        """Make sure that bad sort give an error."""

        with self.assertRaises(ValueError):
            query.QueryBuilder(None).sort(sort=False)
