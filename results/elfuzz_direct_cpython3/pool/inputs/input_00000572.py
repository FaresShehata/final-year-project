"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses as dc
import enum
import functools
import logging
import math
import pickle
import re
import sqlite3
import struct
import sys
import timeit
import typing
from collections.abc import Sequence, Callable, Generator
from itertools import zip_longest
from pathlib import Path
from pprint import pformat
from queue import Queue
from types import FunctionType
from typing import Any, Iterable, List, Tuple, Set, Union, Optional, Type, overload, NoReturn
from uuid import UUID


def seed_01() -> None:
    """
    This is an example of a doctest.

    >>> print('hello')
    hello
    """

    def factorial(n: int) -> int:
        if n == 0 or n == 1:
            return 1
        else:
            return n * factorial(n - 1)

    assert factorial(5) == 120

    # Doctests can be used to test function's docstring.
    assert factorials.__doc__.startswith("This is the built-in ")


async def coroutine_with_logging():
    pass


class BaseException(Exception):
    pass


@dc.dataclass(frozen=True)
class Vector3d:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


# use __slots__ to avoid unnecessary memory overhead for storing class attributes in object's dictionary.
Vector3d.__slots__ = ["x", "y", "z"]


@dc.dataclass(frozen=False)
class Rectangle:
    width: float = 1.0
    height: float = 1.0


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"


Point.__slots__ = ["x", "y"]

p1 = Point(x=3, y=4)
assert isinstance(p1, Point)
assert not hasattr(p1, "__dict__")


class Circle:
    def __init__(self, center: Point, radius: float) -> None:
        self.center = center
        self.radius = radius

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.center!r}, {self.radius!