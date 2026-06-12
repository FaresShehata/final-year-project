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

class Foo:
    _x_classvar: ClassVar[int] = 1

class Bar(Foo):
    _x_classvar: ClassVar[int] = 2

Bar._x_classvar
Foo._x_classvar
isinstance(Foo(), Bar)
isinstance(Bar(), Foo)
isinstance(Bar(), object)

# ── Annotated ────────────────────────────────────────────────────────────────

ANNOTATIONS = Annotated[int, 'a']

# ── __class_getitem__ ────────────────────────────────────────────────────────

vector2D = type[int, int]("Vector2D", (), {}) # or Vector2D = type[int, int](...)?
VecInt = vector2D.__class_getitem__(tuple[int])
VecFloat = VecInt.__class_getitem__(float)

class MyType[A, B, C](object): pass
MyType[int, str].__parameters__
MyType[Any, int, str].__parameters__

# ── __set_name__ ────────────────────────────────────────────────────────────
class A:
    def __set_name__(self, owner: object, name: str) -> None:
        print(f"{owner=}, {name=}")

class B(A):
    attr1 = 222
    attr2 = "abc"

setattr(B, "_attr1", 111)
B.attr1