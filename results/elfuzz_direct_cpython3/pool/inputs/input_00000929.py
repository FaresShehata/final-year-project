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
                break
            case False:
                pass
        print(i * 2)
        i += 1

    with suppress(KeyError):
        print(dict1['key'])

    print("\nTyping Generics")
    print("---------------")
    T = TypeVar("T", bound=int, covariant=True)
    S = TypeVar("S", float, int, covariant=True)


    @dataclasses.dataclass(frozen=True, order=True)
    class OrderedInt(int):
        value1: S = dataclasses.field(compare=False)
        value2: S = dataclasses.field(compare=False)

        def __lt__(self, other: OrderedInt | S) -> bool:
            if isinstance(other, OrderedInt):
                return super(OrderedInt, self).__lt__(other.value1)
            return super(OrderedInt, self).__lt__(other)

        def __le__(self, other: OrderedInt | S) -> bool:
            if isinstance(other, OrderedInt):
                return super(OrderedInt, self).__le__(other.value1)
            return super(OrderedInt, self).__le__(other)

        def __gt__(self, other: OrderedInt | S) -> bool:
            if isinstance(other, OrderedInt):
                return super(OrderedInt, self).__gt__(other.value1)
            return super(OrderedInt, self).__gt__(other)

        def __ge__(self, other: OrderedInt | S) -> bool:
            if isinstance(other, OrderedInt):
                return super(OrderedInt, self).__ge__(other.value1)
            return super(OrderedInt, self).__ge__(other)


    print(isinstance(OrderedInt(1, 2), OrderedInt))
    print(isinstance(OrderedInt(1, 2), int))
    print(isinstance(OrderedInt(1, 2), S))


    @dataclasses.dataclass()
    class A:
        a: int
        b: float = dataclasses.field(default_factory=lambda: 1.0)

    print(A.__annotations__)
    print(A.__dict__)

    a = A(1)
    print(a.a)
    print(a.b)

    with suppress(AttributeError):
        a.c = 2

    for k, v in a.__dict__.items():
        print(k, v)

    @dataclasses.dataclass(order=True)
    class Item:
        item_id: int
        priority: int
        quantity: int