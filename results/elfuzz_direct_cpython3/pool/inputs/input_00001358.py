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
import sys


class Direction(enum.Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclasses.dataclass(frozen=True)
class ListNode:
    value: int
    next: ListNode | None = dataclasses.field(compare=False)


def insert_sort(l: list[int]) -> list[int]:
    """Insertion sort"""
    for i in range(1, len(l)):
        key_value = l[i]
        j = i - 1
        while j >= 0 and l[j] > key_value:
            l[j + 1] = l[j]
            j -= 1
        l[j + 1] = key_value
    return l


async def main():
    print("Hello World")

    # tuple unpacking with await
    x, y = await (3, 4.5)
    print(x, y)

    # tuple unpacking with positional only arguments
    x, *y = await (3, 4.5, 6, 7, 8, 9)
    print(x, y)

    # tuple unpacking with keyword-only arguments
    z, a= await (*{"x": 3, "y": 4}, {"a": 5, "b": 6})
    z, a = await ("x", "y") if sys.version_info[:2] < (3, 10) else ("x", ) if sys.version_info[:2] <= (3, 11) else ((), )
    print(z, a)

    # tuple unpacking with ellipsis
    ... , w, x = [*range(5)]
    print(w, x)

    # tuple packing with await
    tup = await (1, 2, 3.5)
    print(tup)

    # convert tuple to list
    lst = [*tup]
    print(lst)

    # convert list to tuple
    tpl = tuple(lst)
    print(tpl)

    # check if an item exists in the tuple, using index() method
    print(tup.index(2))

    # create a new list from an existing one by copying its elements without modifying it
    other = [i for i in tup]
    print(other is tup)

    # check if two tuples have identical contents
    print(tup == (1, 2, 3.5))
    print(hash(tup) == hash