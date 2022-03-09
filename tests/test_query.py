import logging
import unittest

from mocks import MockDataObject, mock_endpoint

from notional import query

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class QueryBuilderTest(unittest.TestCase):
    """Unit tests for the Query Builder class."""

    def test_EmptyQuery(self):
        qb = query.QueryBuilder(None)
        empty = query.Query()
        self.assertEqual(qb.query, empty)

    def test_BasicNumberConstraint(self):
        mock = mock_endpoint(1000, 100)

        qb = (
            query.QueryBuilder(mock, cls=MockDataObject)
            .filter(property="index", number=query.NumberConstraint(equals=42))
            .limit(1)
        )

        qb.first()

        # self.assertEqual(obj.index, 42)

    def test_NumberRangeConstraint(self):
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

        for obj in qb.execute():
            # self.assertGreater(obj.index, 25)
            # self.assertLessEqual(obj.index, 75)
            pass
