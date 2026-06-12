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

    assert d1 < d3
    assert not (d1 > d3)
    assert d1 <= d3
    assert not (d1 >= d3)

    assert d1 != d3
    assert not (d1 == d3)

    assert d1 < MyDataClass(2, "x")
    assert not (d1 > MyDataClass(2, "x"))
    assert d1 <= MyDataClass(2, "x")
    assert not (d1 >= MyDataClass(2, "x"))

    assert not (MyDataClass(2, "y") < d1)
    assert MyDataClass(2, "y") > d1
    assert not (MyDataClass(2, "y") <= d1)
    assert MyDataClass(2, "y") >= d1

    list_type = [int]
    dict_type = {str: int}
    tuple_type = (float, bool)
    set_type = {str}

    assert isinstance(foo, type(list_type))
    assert isinstance(bar, type(dict_type))
    assert isinstance(d1, type(tuple_type))
    assert isinstance(d1, type(set_type))

    print("============================================")


# ============================== SEED 04 ======================================


def seed_04():
    print("\n\n================= Seed 04 =================")

    class Foo:
        pass

    class Bar(Foo):
        pass

    class Baz(Foo):
        pass

    foo = Foo()
    bar = Bar()
    baz = Baz()

    assert isinstance(foo, Foo)
    assert isinstance(foo, Bar)
    assert isinstance(foo, Baz)

    assert isinstance(bar, Foo)
    assert isinstance(bar, Bar)
    assert isinstance(bar, Baz)

    assert isinstance(baz, Foo)
    assert isinstance(baz, Bar)
    assert isinstance(baz, Baz)

    assert not isinstance(foo, object)
    assert isinstance(foo, object)

    assert not isinstance(bar, object)
    assert isinstance(bar, object)

    assert not isinstance(baz, object)
    assert isinstance(baz, object)

    print("============================================")


# ============================== SEED 05 ======================================


def seed_05():
    print("\n\n================= Seed 05 =================")

    class Foo:
        pass

