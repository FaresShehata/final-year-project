"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyList(list):
    items_per_line: ClassVar[int] = 3
    item_separator: ClassVar[str] = ", "

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyClass:
    attribute_1: ClassVar[str] = "Hello"
    attribute_2: ClassVar[str] = "World"

# ── ClassVar ─────────────────────────────────────────────────────────────────

class MyString(str):
    def upper_case(self) -> str:
        return self.upper()

# ── VarArg and Kwarg ─────────────────────────────────────────────────────────

def var_arg_func(*args: Any) -> None:
    print(args)
    for arg in args:
        print(arg.__class__.__name__)

var_arg_func()
var_arg_func(1)
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

# ── __class_getitem__ ────────────────────────────────────────────────────────

class MyClassWithGeneric(Generic[T]):
    @classmethod
    def __class_getitem__(cls, params: P) -> TypeVar("MyClassWithGeneric[P.T]") & T:
        return cls(params)

    def __init__(self, x: T, y: T) -> None:
        self.x = x
        self.y = y

mwg1 = MyClassWithGeneric[int](1, 2)
mwg2 = MyClassWithGeneric[float](3.0, 4.0)

# ── __set_name__ ─────────────────────────────────────────────────────────────

class MyClassWithSetters:
    _some_attr: int = 1

    @property
    def some_attr(self) -> int:
        return self._some_attr

    @some_attr.setter
    def some_attr(self, new_value: int) -> None:
        """Setter docstring."""
        self._some_attr = new_value

    def set_some_other_attr(self, value: int) -> None:
        """
        This is another setter.
        It takes a single argument `value` of type int and sets the `_other_attr`
        instance variable to this value.

        :param value: The new value for the `_other_attr` attribute.
        :return: None
        """
        self._other_attr = value

# ─