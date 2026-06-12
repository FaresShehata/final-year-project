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


class MetricsRecord(TypedDict):
    latency_ms: float
    requests:   int


# ── ClassVars ────────────────────────────────────────────────────────────────

class Color(NamedTuple):
    r: int; g: int; b: int; a: int = 255


class Settings(Generic[T]):
    default_value: T
    values: tuple[T, ...]
    
    def __init__(self, value: T) -> None:
        self.value = value
    
    def __repr__(self) -> str:
        return f"<{type(self).__name__} value={repr(self.value)}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value



# ── Typing Extras ────────────────────────────────────────────────────────────


def foo(x: Annotated[int, "foo", math.exp]) -> Annotated[float, "bar"]:
    ...
    

def bar(x: Annotated[A := int, "baz"]) -> Annotated[B := A + x, "qux"]:
    ...


def baz() -> Annotated[C := (lambda x: x)[1], "fizz"]:
    ...


class Bar(Annotated[D := B, "buzz"]):
    pass


def quux(
    x: Annotated[E := int, "spam"],
    y: Annotated[F := E * 2, "eggs"],
) -> Annotated[G := F - 3, "toast"]:
    ...


def spam() -> Annotated[H := float, "bacon"]:
    ...


class Spam(Generic[I := H]):
    def __init__(self, x: Annotated[J := I, "hash"]) -> None:
        self.x = x
        
    def eggs(self, x: Annotated[K := J, "cheese"]) -> Annotated[L := K ** 2, "and"]:
        ...
        
    @property
    def toast(self) -> Annotated[M := L, "spam"]:
        return M
    

# ── __class_getitem__ ────────────────────────────────────────────────────────

S = TypeVar("S")

class Foo(Generic[S]):
    def __class_getitem__(cls, item: S) -> Foo[S]:
        return cls(item)


class Bar(Foo["Bar" | "Baz"]):
    ...


class Baz(Foo["Foo[Bar]", "Bar", "Baz"]):
    ...


assert issubclass(Bar, Foo)
assert issubclass(Baz, Foo)

try:
    _ = Foo[int]()
except TypeError:
    assert True
else:
    assert False


# ── __set_name__ ────────────────────────────────────────────────────────────

class BaseClass:
    @classmethod
    def __prepare__(
        cls,
        meta: type[Any],
        name: str,
        globals_: dict[str, Any],
        locals_: dict[str, Any],
    ) -> dict[str, Any]:
        return {"base": True}
    
    
    def __init__(self, field1: str, *, field2: int, field3: float):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        
        
    @property
    def field4(self) -> str:
        return "field4"
        
        
    class Subclass(BaseClass):
        pass
        
        
BaseClass.__dict__["base"]
BaseClass("a", field2=1, field3=2.0).subfield1
BaseClass.subclass_field1
BaseClass().nonexistent_property


# ── __init_subclass