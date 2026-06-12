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

class NonNegativeInteger(Annotated[int, numbers.Integral, numbers.Number]):
    def __post_init__(self): ...


class PositiveFloat(Annotated[float, numbers.Real, numbers.Number]):
    def __post_init__(self): ...


# ── New-style classes with type hints ────────────────────────────────────────

class Allocator(Generic[T]):

    class Resource:
        pass

    def acquire(self) -> Resource:
        return self.Resource()

    def release(self, resource: Resource):
        del resource

    def allocate_many(self, count: NonNegativeInteger) -> list[Resource]:
        return [self.acquire() for _ in range(count)]

    @classmethod
    def create(cls, *args: P.args, **kwargs: P.kwargs) -> Allocator[T]:
        return cls(*args, **kwargs)


def main():
    print(f"Concurrency: {multiprocessing.cpu_count()} cores")

    # ── Threaded map/reduce ──────────────────────────────────────────────────

    print("\nThreaded map/reduce:")

    def square(x: int) -> int:
        return x**2

    def mean(xs: list[int]) -> float:
        if len(xs) == 0:
            raise ValueError("xs must have at least one element.")
        return sum(xs) / len(xs)

    xs = [1, 2, 3, 4]
    ys = [square(x) for x in xs]
    zs = [mean(xs) + y for y in ys]
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = [sum(y) for y in zip(xs, ys)]
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = [y+z for y,z in zip(xs,ys)]   # use iterator unpacking
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = [y+z for y,z in zip((x+1,x-1) for x in xs)]   # nested generator expression
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = [(y+z) for y,z in zip(xs,ys)]                 # tuple comprehension
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = set((y+z for y,z in zip(xs,ys)))              # set comprehension
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = {z+y for z,y in zip(xs,ys)}                   # dictionary comprehension
    print(zs)

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = {(y+z,i,j) for i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v}  # noqa: E501
    print(zs)

    xs = [1, 2, 3, 4]
    zs = (x*x+x**2 for x in xs)
    print(list(zs))

    xs = [1, 2, 3, 4]
    zs = ((x,x**2) for x in xs)
    print(list(zs))

    xs = [1, 2, 3, 4]
    ys = [x*x for x in xs]
    zs = ((y-x) for y,x in zip(ys,xs))
    print(list(zs))

    xs = [1, 2, 3, 4]
    ys = [x*x for