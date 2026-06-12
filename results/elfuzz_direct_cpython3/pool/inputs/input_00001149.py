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
import sys
import time


def main():
    """Entry point."""

    print("Async await")
    # https://docs.python.org/3/library/asyncio-task.html#task-scheduling
    asyncio.run(async_main())

    print("\nProtocols")
    print(Protocol.__mro__)
    print(Polygon.__mro__)

    print("\ndata classes")
    print(dataclass_simple())
    print(dataclass_with_slots())

    print("\nslots")
    print(slots_simple())
    print(slots_with_slots())

    print("\npattern matching")
    match = "Hello"
    if isinstance(match, str):
        print(f"match is a string: {match}")
    elif isinstance(match, int):
        print(f"match is an integer: {match}")

    print(pattern_matching_match_type())

    print("\ngenerics")
    print(typing_generics_named_tuple())
    print(typing_generics_list())
    print(typing_generics_dict())
    print(typing_generics_set())
    print(typing_generics_frozenset())
    print(typing_generics_tuple())
    print(typing_generics_sequence())
    print(typing_generics_str)
    print(typing_generics_bytes)

    print("\nwalrus operator")
    print(walrus_operator_basic())
    print(walrus_operator_complex())

    print("\nexception group")

    try:
        raise ValueError("value error")
    except Exception as exc:
        print(ExceptionGroup("group", [exc]))

    print("\nExceptionGroup")


@dataclasses.dataclass(order=True, frozen=False)
class Polygon(enum.Enum):
    name = "Polygon"


@dataclasses.dataclass(order=True, frozen=True)
class Point:
    x: float
    y: float


@dataclasses.dataclass(order=True, slots=True)
class PointSlots:
    x: float
    y: float


@dataclasses.dataclass(order=True, frozen=False)
class DataClassSimple:
    a: int
    b: int
    c: int


@dataclasses.dataclass(order=True, frozen=True)
class DataClassWithSlots:
    a: int
    b: int
    c: int


@dataclasses.dataclass(order=True, frozen=True)
class ABC:
    a: int
    b: int


def dataclass_simple():
    return DataClassSimple(a=1, b=2, c=3)


def dataclass_with_slots():
    return DataClassWithSlots(a=1, b=2if __name__ == "__main__":
    main()