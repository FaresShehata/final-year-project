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

    print("\ndataclasses")
    @dataclasses.dataclass()
    class Point:
        x: int
        y: int
    p1 = Point(x=5, y=4)
    p2 = Point(x=3, y=7)
    assert str(p1) == "(5, 4)"
    assert repr(p1) == "Point(x=5, y=4)"

    print("\nprotocols")
    class MyIterable(Iterator[int]):
        def __iter__(self):
            yield from range(8)
    mi = MyIterable()
    print(list(mi))

    print("\ndataclasses and __slots__")
    @dataclasses.dataclass(frozen=True, slots=True)
    class SlottedDataClass:
        foo: str
        bar: bool
    sd = SlottedDataClass(foo="a", bar=False)
    sd.foo = "b"  # ERROR (read-only)

    print("\nstructural pattern matching")
    class Shape:
        kind: str
    class Circle(Shape):
        radius: float
    class Square(Shape):
        side_length: float

    shapes = [Circle(radius=2), Square(side_length=3)]
    for shape in shapes:
        match shape:
            case Square(side_length=sq_side):
                print(f"A square with side length {sq_side}")
            case Circle(radius=c_radius):
                print(f"A circle with radius {c_radius}")

   