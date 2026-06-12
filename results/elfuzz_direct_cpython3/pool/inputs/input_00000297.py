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
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"

# ── ParamSpec ────────────────────────────────────────────────────────────────

class MyFunc(Generic[T]):
    def __call__(self, arg1: T, /, *args, **kwargs): ...

f = MyFunc[int]()
print(get_type_hints(f))

# ── TypedDict ────────────────────────────────────────────────────────────────

record = UserRecord(id=17, name="John Doe", email="<EMAIL>", active=True, metadata={"gender": "male"})
print(record["active"])

for key, val in record.items():
    print(key, val)

for key in record.keys():
    print(key)

for val in record.values():
    print(val)

if "id" in record:
    print("has 'id'")  # noqa: T001

v: int = record["id"]
print(v)

# ── Annotated ────────────────────────────────────────────────────────────────

sensors = [
    Sensor(label="CPU Temperature", reading=38.97),
    Sensor(label="GPU Temperature", reading=51.37),
    Sensor(label="RAM Usage", reading=0.124),
]

for sensor in sensors:
    try:
        print(sensor.reading * 100)
    except TypeError:
        print(f"{sensor.label}: unsupported operand type(s) for *:")
        continue

# ── ABCs ────────────────────────────────────────────────────────────────────

assert isinstance(base64.b64encode(b"\x00\xff"), bytes)

with open(pathlib.Path(__file__).parent.parent.joinpath(
    "test.txt"
), encoding="utf-8") as fp:
    content = fp.read()

content = textwrap.dedent(content).strip()
print(content)

chunks = [chunk.strip() for chunk in content.split("\n\n")]
print(chunks[0])

# ── pathlib ──────────────────────────────────────────────────────────────────

cwd  = pathlib.Path.cwd().resolve()
home = cwd.parents[0].joinpath(".local").joinpath("share").expanduser()

if home.exists():
    with open(home.joinpath("example.txt")) as fp:
        lines = fp.readlines()

lines = "\n".join(lines)
fp = open(home.joinpath("example.txt"))
data = io.StringIO(fp.read())
print(data.read())

fp.seek(0)
print(fp.read(4))
print(fp.tell    @property
