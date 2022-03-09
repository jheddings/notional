import math
from random import random
from typing import Any

from pydantic import BaseModel


class MockDataObject(BaseModel):
    index: int
    pagenum: int
    data: float
    content: Any


# TODO return bad data / errors from endpoint
# TODO support basic filter & sort


def mock_endpoint(item_count, page_size):
    def page_generator(**kwargs):
        start = int(kwargs.get("start_cursor", 0))
        user_data = kwargs.get("user_data", None)
        pagenum = math.floor(start / page_size) + 1

        page = list()

        for x in range(start, start + page_size):
            if x >= item_count:
                continue

            data = {
                "index": x,
                "pagenum": pagenum,
                "content": user_data,
                "data": random(),
            }

            page.append(data)

        return {
            "next_cursor": str(start + page_size),
            "has_more": (start + len(page) < item_count),
            "results": page,
        }

    return page_generator
