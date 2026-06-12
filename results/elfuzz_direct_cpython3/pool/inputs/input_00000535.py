"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence, Set
from dataclasses import dataclass, field
from functools import partial
from inspect import isasyncgenfunction, iscoroutinefunction, signature
from itertools import chain, cycle, dropwhile, groupby, tee
from types import GeneratorType, UnionType
from types import ModuleType as _ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    cast,
)
from warnings import warn


def main() -> None:
    """Entry point"""
    # seed_01()
    # seed_02()
    # seed_03()
    # seed_04()
    # seed_05()
    # seed_06()
    # seed_07()
    # seed_08()


# ============================== SEED 01 ======================================


def seed_01():
    print("\n\n================= Seed 01 =================")
    class A(ABC):
        @abstractmethod
        def m(self) -> int: ...

    x = A()

    try:
        x.m()
    except NotImplementedError as e:
        print(e)

    print("============================================")


# ============================== SEED 02 ======================================


def seed_02():
    print("\n\n================= Seed 02 =================")

    def f(x: float | str) -> int:
        if isinstance(x, str):
            return len(x)
        else:
            return int(x)

    assert f("hello") == 5
    assert f(3.14) == 3

    print("============================================")


# ============================== SEED 03 ======================================


def seed_03():
    print("\n\n================= Seed 03 =================")

    def foo(x: int) -> int:
        pass

    def bar(s: str) -> str:
        pass

    @dataclasses.dataclass(order=True, frozen=False)
    class MyDataClass:
        x: int
        s: str

    d1 = MyDataClass(1, "a")
    d2 = MyDataClass(2, "b")
    d3 = MyDataClass(1, "c")

    assert d1 < d2
    assert not (d1 > d2)
    assert d1 <= d2
    assert not (d1 >= d2)

    assert d1 <= d3 and d1 < d3
    assert d3 == d3
    assert d3 != d2
    assert not (d1 < d3 or d3 < d1)
    assert not (d1 > d3 or d3 > d1)

    assert hash(d1) != hash(d2)

    print("============================================")


# ============================== SEED 0