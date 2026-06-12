"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    Sequence,
    TypeAlias,
    TypeGuard,
)

if TYPE_CHECKING:
    from collections.abc import MutableMapping

from . import utils


class _Enum(Protocol):
    def __str__(self) -> str:
        ...


# noinspection PyMissingOrEmptyDocstring
class _Order(enum.IntEnum):
    FIRST = -1
    LAST = 1


def _listify(value):
    if isinstance(value, list):
        return value
    return [value]


async def main():
    # Walrus Operator
    a, b = await (task_a(), task_b())
    print(a + b)
    # The above is equivalent to the following:
    a_result, b_result = await asyncio.gather(task_a(), task_b())
    print(a_result + b_result)

    # Dataclasses
    @dataclasses.dataclass(slots=True)
    class Point:
        x: int
        y: int

    p = Point(x=3, y=-4)
    assert utils.hash_object(p) == hash((p.x, p.y))
    assert p == Point(x=p.x, y=p.y)
    assert not (Point(x=3, y=-4) != Point(x=3, y=-5))

    point = dataclasses.replace(Point(x=1), x=3)
    assert point.__match_args__ == ("x", "y") and point.__annotations__ == {
        "x": int,
        "y": int,
    }
    assert repr(point) == "Point(x=3, y=-4)"
    assert point == Point(x=3, y=-4)
    assert hash(point) == hash((point.x, point.y))

    # Asyncio with Generators
    async def gen():
        yield 1
        yield 2
        yield 3
        yield 4

    async for i in gen():
        assert i in (1, 2, 3, 4)

    # Structural Pattern Matching
    def parse_json(data) -> None | dict[str, object]:
        match data:
            case {"name": name}:
                return {"name": name}
            case {"key": key} as obj:
                return {key: obj[key]}
            case {}:
                return {}
            case _:
                raise ValueError("Unknown JSON format")

    assert parse_json({"name": "John"}) == {"name": "John"}
   