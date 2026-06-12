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
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{obj}.{self.pub} must be {constraint}")
        setattr(obj, self.priv, value)


def constrained(min_: int = ..., max_: int = ...,
                min_inclusive: bool = True, max_inclusive: bool = True):
    assert min_ <= max_, "min must be less than or equal to max"

    def check(val):
        if val >= min_ and (not min_inclusive or val != min_) and \
           val <= max_ and (not max_inclusive or val != max_):
            return True
        else:
            return False

    def infer_constraints(typ):
        if typ == Literal[min_]: return check(min_)
        elif typ == Literal[max_]: return check(max_)
        else:                      return check

    def make_constraint(clss, typ):
        try:      return clss(typ)
        except:   return infer_constraints(typ)

    return Annotated[int, make_constraint(_MinConstraint, min_), make_constraint(_MaxConstraint, max_)],
            Annotated[float, make_constraint(_MinFloatConstraint, min_), make_constraint(_MaxFloatConstraint, max_)],

class _MinConstraint(NamedTuple):
    value: int

    def __call__(self, n: int) -> bool:
        return n > self.value

class _MaxConstraint(NamedTuple):
    value: int

    def __call__(self, n: int) -> bool:
        return n < self.value

class _MinFloatConstraint(NamedTuple):
    value: float

    def __call__(self, n: float) -> bool:
        return n > self.value

class _MaxFloatConstraint(NamedTuple):
    value: float

    def __call__(self, n: float) -> bool:
        return n < self.value


class _HasTypeConstraint(NamedTuple):
    type_: type[Any]
    message: str

    def __call__(self, obj: Any) -> bool:
        return isinstance(obj, self.type_)


# ── TypeVars and ParamSpec ────────────────────────────────────────────────────

V  = TypeVar("V")
K  = TypeVar("K")
VK = ParamSpec("VK")
KV = ParamSpec("KV")


# ── Decorators ────────────────────────────────────────────────────────────────


def deprecated(
    reason: Literal["deprecated"] | str = "deprecated",
    *,
    replacement: str | None = None,
    alternative: str | tuple[str, ...] | None = None,
    alternative_msg: str | None = None,
    category: type[Exception] = DeprecationWarning,
    stacklevel: int = 1,
    added: Literal["1.7"] | str = "1.7",
) -> Callable[[Callable[P, T]], Callable[P, T]]:

    def decorator(func: Callable[P, T]) -> Callable[P, T]:

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            msg = ""
            if reason == "deprecated":
                msg = f"This function has been deprecated"
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Disassembling the standard library ────────────────────────────────────────


def dump_stdlib():
    """Show some examples of how to use dis."""
    import binascii
    import functools
    import hashlib
    import hmac
    import json
    import math
    import os
    import random
    import secrets
    import shutil
    import string
    import timeit

    print("-" * 80)
    print(f"{binascii.binascii.__name__:>36} bytecode:")
    print(annotated_disassembly(binascii.binascii))
    print()

    print("-" * 80)
    print(f"{functools.lru_cache.__name__:>36} bytecode:")
    print(annotated_disassembly(functools.lru_cache))
    print()

    print("-" * 80)
    print(f"{hashlib.sha256.__name__:>36} bytecode:")
    print(annotated_disassembly(hashlib.sha256))
    print()

    print("-" * 80)
    print(f"{hmac.compare_digest.__name__:>36} bytecode:")
    print(annotated_disassembly(hmac.compare_digest))
    print()

    print("-" * 80)
    print(f"{json.dumps.__name__:>36} bytecode:")
    print(annotated_disassembly(json.dumps))
    print()

    print("-" * 80)
    print(f"{math.isclose.__name__:>36} bytecode:")
    print(annotated_disassembly(math.isclose))
    print()

    print("-" * 80)
    print(f"{os.kill.__name__:>36} bytecode:")
    print(annotated_disassembly(os.kill))
    print()

    print("-" * 80)
    print(f"{random.shuffle.__name__:>36} bytecode:")
    print(annotated_disassembly(random.shuffle))
    print()

    print("-" * 80)
    print(f"{secrets.token_bytes.__name__:>36} bytecode:")
    print(annotated_disassembly(secrets.token_bytes))
    print()

    print("-" * 80)
    print(f"{timeit.repeat.__name__:>36} bytecode:")
    print(annotated_disassembly(timeit.repeat))
    print()

    print("-" * 80)
    print(f"{shutil.copyfileobj.__name__:>3    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

