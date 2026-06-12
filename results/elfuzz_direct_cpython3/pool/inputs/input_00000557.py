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
        case list([]):
            print("empty list")
        case set([]):
            print("empty set")
        case _:
            print("other")

    match_obj = [1]
    match match_obj:
        case []:
            print("empty list")
        case [_]:
            print("single element list")
        case other:
            print(other)


    class Foo:
        def __repr__(self) -> str:
            return "<Foo>"

    match_obj = [1, 2, 3]
    match match_obj:
        case [first, second, third]:
            print(first + second + third)
        case [Foo(), *rest]:
            print(rest[0])


    match_obj = {"key": "value"}
    match match_obj:
        case {'key': 'value'}:
            printvar_arg_func(1)
var_arg_func(True)
var_arg_func([1, 2])
var_arg_func(MyClass())
var_arg_func(MyString("abc"))

def kwarg_func(**kwds: Any) -> None:
    print(kwds)
    for key, val in kwds.items():
        print(key, val.__class__.__name__)

kwarg_func()
kwarg_func(name="Alice", age=30)
kwarg_func(person={"name": "Bob", "age": 25})
kwarg_func(items=[1, 2, 3])

# ── overload --- (Optional[Tuple[Any, ...]]) ─────────────────────────────────

from typing import overload

@overload
def my_function(param: tuple[int, str]) -> str: ...
@overload
def my_function(param: tuple[int, ...]) -> int: ...

def my_function(param: tuple[int, ...]) -> int:
    return sum(param)

my_tuple = (1, 2, 3)
print(my_function(my_tuple))

# ── Annotated ────────────────────────────────────────────────────────────────

def validate_string(value):
    try:
        repr(value)
        return value
    except Exception as e:
        raise ValueError(f"Invalid string: {e}") from e

def validate_int(value):
    if isinstance(value, int):
        return value
    else:
        raise TypeError("Expected an integer")

annotated_str: Annotated[str, validate_string] = "hello world"
annotated_int: Annotated[int, validate_int] = 42

try:
    invalid_anonstr: Annotated[str, int] = 100 # type: ignore
except TypeError as e:
    print(e)

# ── get_type_hints ───────────────────────────────────────────────────────────

def foo(x: int, y: str) -> float:
    pass

type_hints = get_type_hints(foo)
for param_name, hint in type_hints.items():
    print(f"{param_name}: {hint}")

# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type("foo_bar")

