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
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    def __init__(self, *constraints: Callable[[Any], bool]) -> None:
        self.constraints = tuple(constraints)
    
    def __get__(self, instance: object, owner: type[Any]) -> SuperSet:
        return SuperSet(*instance.__dict__[owner.__name__].values()) # type: ignore
    
    def __set__(self, instance: object, value: SuperSet) -> None:
        for key in value:
            if not all(constraint(value[key]) for constraint in self.constraints):
                raise TypeError(f"Invalid {value} for key '{key}'")
        
        instance.__dict__[owner.__name__][None] = value # type: ignore


class SuperSet(Generic[T]):
    def __init__(self, *values: T) -> None:
        values = [v for v in values if isinstance(v, self)]
        super().__setattr__("super_set", frozenset(values))
        super().__setattr__("values", frozenset(values)) # type: ignore
    
    
    @classmethod
    def from_iterable(cls, iterable: Iterable[T]) -> Self[T]:
        return cls(*iterable)


# ── ParamSpec ────────────────────────────────────────────────────────────────

def f(x: int, y: int = 1) -> int:
    """Docstring."""
    pass


def g(a: ParamSpec["A"], b: ParamSpec["B"]) -> A + B | float:
    return a + b # type: ignore


def h(c: ParamSpec["C"]) -> C:
    return c # type: ignore # mypy says 'C' has no attribute '__call__'
    

# ── ClassGetItem ────────────────────────────────────────────────────────────

class Foo:
    def bar(self) -> str:
        return "bar"

    def baz(self) -> str:
        return "baz"


foo = Foo()
print(foo['bar']) # prints 'bar'
print(foo.bar)    # prints <bound method Foo.bar of <__main__.Foo object at ...>>
print(foo.baz)    # prints <function Foo.baz at ...>

foo['bar']()      # prints 'bar'


class Bar(Foo):
    def qux(self) -> str:
        return "qux"
    
    
@dataclasses.dataclass
class Baz:
    x: int


b = Baz(3)
print(b.x)