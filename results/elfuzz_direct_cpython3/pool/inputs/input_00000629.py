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
import traceback
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence, Set, Sized
from contextlib import suppress
from datetime import timedelta
from functools import partial
from itertools import chain, islice
from logging import DEBUG, INFO, WARNING
from numbers import Integral
from pathlib import Path
from types import GenericAlias, NoneType, TracebackType
from typing import Any, ClassVar, Literal, TypedDict, TypeGuard, TypeVar, Union, cast
from warnings import warn


class BoringException(Exception):
    pass


def dummy():
    """This function is used to make the example more readable."""
    return "dummy"


def run():
    """main entry point"""
    print("##############################")
    print("#         Seed 02            #")
    print("##############################\n")

    print("asyncio")
    a = asyncio.run(asyncio.sleep(1))
    assert a == 1.0

    await asyncio.sleep(1)
    print("Done!")

    print("\nProtocols")
    print("---------")

    class P:
        def __init__(self, x: int):
            self.x = x

        @classmethod
        def from_dict(cls, d: dict) -> P:
            return cls(d["x"])

    p = P.from_dict({"x": 1})

    class P2(P):
        def __init__(self, x: int, y: str):
            super().__init__(x)
            self.y = y

    p2 = P2.from_dict({"x": 1, "y": "abc"})
    print(p2.x)
    print(p2.y)

    class P3(P):
        pass

    p3 = P3.from_dict({"x": 1}) # type: ignore
    print(p3.x)

    with suppress(TypeError): # suppresses the error message
        P3.from_dict({}) # type: ignore

    print("\nData Classes")
    print("------------")

    @dataclasses.dataclass(eq=True, frozen=False)
    class Person:
        name: str
        age: int

    person = Person('Alice', 30)
    person2 = Person('Alice', 30)

    print(dataclasses.fields(Person))


    @dataclasses.dataclass(slots=True)
    class SlotsPerson:
        name: str
        age: int

    slots_person = SlotsPerson('Alice', 30)
    slots_person.name = 'Bob'

    print("\nStructural Pattern Matching")
    print("---------------------------")

    match_obj = 1

    match match_obj:
        case 1:
            print("One")
        case 2:
            print("Two")
        case _:
            print("Something else")

    match_obj_2 = {"a": 1}

    match match_obj_2:
        case {'a': _, **kwargs}:
            print(kwargs)


    @dataclasses.dataclass(frozen=True)
    class Point:
        x: float
        y: float

    pt = Point(1.0, 2.0)
    
    match pt:
        case Point(x=0, y=_):
            print("On the x-axis at {}".format(x))
        case Point(x=_, y=0):
            print("On the y-axis at {}".format(y))
        case Point(x=0, y=0):
            print("At the origin")
        case Point():
            print("Somewhere in space")


    @dataclasses.dataclass
    class Rectangle:
        p1: Point
        p2: Point
    
    rec = Rectangle(Point(1, 2), Point(4, 5))

    match rec.p1:
        case Point(x=a, y=1):
            print(a)
        case Point(x=1, y=b):
            print(b)
        case Point() if a > b:
            print("p1's x is bigger than p2's x")
        case Point():
            raise ValueError("Point must be on the x or y axis.")

    print("\nWalrus Operator")
    print("---------------")

    i = 0
    while True:
        match i < 5:
            case True:
                if i % 2 == 0:
                    continue
                yield i
            case False:
                break
                
        i += 1


    @dataclasses.dataclass
    class Point:
        x: float
        y: float
    
    points = [Point(1.0, 2.0), Point(2.0, 4.0)]

    for point in points:
        match point:
            case Point(x=y, y=x):
                print(point)
            case Point(x=x, y=y):
                print((point.x, point.y))
            case Point(x=x, y=y) if x > y:
                print((point.x, point.y))
            case Point(x=x, y=y) if x < y:
                print((point.x, point.y))
            case Point(x=x, y=y) if x
# ── Annotated ────────────────────────────────────────────────────────────────

def validate_string(value):
    try:
        repr(value)
        return value
