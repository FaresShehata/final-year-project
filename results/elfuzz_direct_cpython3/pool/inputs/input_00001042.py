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
import types
import warnings
from abc import ABCMeta
from collections import (
    ChainMap,
    Counter,
    deque,
    OrderedDict,
    namedtuple,
    UserDict,
    UserList,
    UserString,
)
from concurrent.futures import Future as ConcurrentFuture
from contextlib import suppress
from functools import cached_property, partialmethod, reduce
from inspect import Parameter, Signature, signature
from itertools import chain, count, cycle
from pathlib import Path
from numbers import Integral, Real
from types import MappingProxyType
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    TypeAlias,
    overload,
)
from urllib.parse import quote_plus
from uuid import UUID

try:
    from typing_extensions import Protocol
except ImportError:  # pragma: no cover
    from typing import _Protocol as Protocol

warnings.filterwarnings("ignore", category=DeprecationWarning)


# ─── SEED 02 ────────────────────────────────────────────────────────────────────

warnings.simplefilter(action="ignore")


async def seed_02():
    """
    Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
              walrus operator, typing generics, exception groups, ExceptionGroup
    """

    print('\n\nSEED 02')

    assert not (True and False and True), "Logical AND"
    assert (not True or False) and True, "Logical OR"
    assert ((True and False) or (False or True)) == (False or (False or True)), "DeMorgan's laws"

    assert bool(False and True) is False, "Logical AND with bools"

    if 456.789:
        pass

    if 'abc':
        pass

    if {'key': 'value'}:
        pass

    class Person:

        name: str
        age: int

        def __repr__(self):
            return f'Person(name="{self.name}", age={self.age})'

    jake = Person()
    jake.name = 'Jake'
    jake.age = 20
    print(jake, type(jake))
    print(repr(jake), type(repr(jake)), type(jake).__name__)

    class Car:
        brand: str
        model: str
        year: int

        def __repr__(self) -> str:
            return f'{self.brand} {self.model} ({str(self.year)})'

        def __eq__(self, other: Car) -> bool:
            return self.brand == other.brand and self.model == other.model and self.year == other.year

    ford = Car()
    ford.brand = 'Ford'
    ford.model    #   True
    #   False
    #   False
    #   True

    print('OK')


# ── Currying ────────────────────────────────────────────────────────────────

class CurriedFunction(Callable[[A], Callable[[B], Callable[[C], A]]]):
    """Currying function."""

    def __init__(self, func: Callable[[A, B, C], A]) -> None:
        self.__func = func

    def __call__(self, a: A, b: B, c: C) -> A:
        return self.__func(a, b, c)

    @classmethod
    def curry(cls, func: Callable[..., A]) -> CurriedFunction[A]:
        """Curries the given function."""
        return cls(func)


@functools.lru_cache()
def add(x: int, y: int) -> int:
    """Add two integers."""
    return x + y


add_curried = CurriedFunction.curry(add)
print(type(add(1, 2)))
print(type(add(1)))
print(type(add_curried))

a = add(1, 2)
b = add_curried(1)(2)
c = add(1)(2)(3)

print(a, b, c)
# Output:
#   <class 'int