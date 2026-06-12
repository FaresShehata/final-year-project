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

class User(TypedDict):
    username: str
    password: str
    is_awesome: bool

# ── ParamSpec ────────────────────────────────────────────────────────────────

def foo(*args: P.args, **kwargs: P.kwargs) -> tuple[P.args, P.kwargs]:
    ...

def bar(x: int, y: str = 'y', z: float = .123) -> float:
    return x + (y or "") + str(z)
print(get_type_hints(bar))

# ── Annotated ────────────────────────────────────────────────────────────────

Annotated[int, ...]
Annotated[int, ..., "Some docstring"]

@dataclasses.dataclass
class MyClass(Annotated[int]):
    a: int
    b: Annotated[float, "A fixed value"]
    c: Annotated[float, ..., 3.14]

# ── get_type_hints ──────────────────────────────────────────────────────────

def my_func(a: Annotated[int]) -> Annotated[int]: ...
get_type_hints(my_func)

# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type(int())

# ── ClassVar ────────────────────────────────────────────────────────────────

class Foo(ClassVar[int]): ...

Foo: int = 1

# ── _X__dict__() ────────────────────────────────────────────────────────────

class A:
    def __x_dict__(self) -> dict[str, Any]:
        return {"foo": self.foo}

class B(A):
    def __x_dict__(self) -> dict[str, Any]:
        return {"bar": super().__x_dict__()}

b = B()
b.__x_dict__()

# ── _X__init__() ────────────────────────────────────────────────────────────

class X(Generic[T]):
    def __init__(self, t: T) -> None:
        self.t: T = t

x = X[int]()
x.t == 1

# ── _X__new__() ─────────────────────────────────────────────────────────────

class A(Generic[T]):
    @classmethod
    def __new__(cls, *args: P.args, **kwargs: P.kwargs) -> A[T]:
        return object.__new__(cls)

    def __init__(self, t: T) -> None:
        self.t: T = t

a = A[int](1)

# ── __init_subclass__ ────────────────────────────────────────────────────────

class Foo(object):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.name = "Foo"

class Bar(Foo):
    name: str
Bar().name
    
# ── CONCURRENT MODULES ───────────────────────────────────────────────────────

def process_data(data: str) -> str:
    return data.upper()

executor = ThreadPoolExecutor(max_workers=2)
task = executor.submit(process_data, "Hello, World!")
result: str = task.result()

with ThreadPoolExecutor() as pool:
    results: list[str] = []
    for result in pool.map(process_data, ["Hello, World!", "Goodbye, World!"]):
        results.append(result)

def concatenate_strings(strings: list[str]) -> str:
    return "".join(strings)

strings_to_concatenate = ["abc", "def", "ghi"]
pool = ThreadPoolExecutor(max_workers=2)
results = [pool.submit(concatenate_strings, strings[:2]) for strings in zip(strings_to_concatenate)]
for future in as_completed(results):
    print(future.result())
    
def do_work(i: int) -> int:
   ANNOTATIONS = Annotated[int, 'a']

# ── __class_getitem__ ────────────────────────────────────────────────────────

vector2D = type[int, int]("Vector2D", (), {}) # or Vector2D = type[int, int](...)?
VecInt = vector2D.__class_getitem__(tuple[int])
VecFloat = VecInt.__class_getitem__(float)

class MyType[A, B, C](object): pass
MyType[int, str].__parameters__
MyType[Any, int, str].__parameters__

# ── __set_name__ ────────────────────────────────────────────────────────────

class BaseClass:
