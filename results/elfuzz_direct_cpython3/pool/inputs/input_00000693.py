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

sensor = Sensor(label="Humidity", reading=38.7)
assert sensor.label == "Humidity"
assert sensor.reading == 38.7


# ── string.Format ────────────────────────────────────────────────────────────

class Color(NamedTuple):
    r: int
    g: int
    b: int

format_spec = "{color.r}-{color.g}-{color.b}"
template = textwrap.dedent(
"""\
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
      <rect fill="#{:>s}" width="{w}" height="{h}" />
    </svg>
""")
data = template.format(color=Color(r=192, g=192, b=0), w=100, h=100, width=100, height=100)
print(data)


# ── threading ────────────────────────────────────────────────────────────────

start  = time.perf_counter()
threads: list[threading.Thread] = []
for i in range(10):
    thread = threading.Thread(target=lambda: print(i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
end = time.perf_counter()
print(end - start)
wait = sum(thread.join(timeout=1) for thread in threads)
print(wait)


# ── multiprocessing ─────────────────────────────────────────────────────────

procs = [multiprocessing.Process(target=lambda: print(i)) for i in range(10)]
for proc in procs:
    proc.start()
for proc in procs:
    proc.join()


# ── contextlib ──────────────────────────────────────────────────────────────

context = contextlib.nullcontext()
with context:
    assert context is contextlib.nullcontext


# ── numbers abstract base classes ────────────────────────────────────────────

x = 0
while True:
    try:
        x += 1 / 2 ** x
    except OverflowError:
        break
print(x)


# ── csv ─────────────────────────────────────────────────────────────────────-

csv_path = "/tmp/test.csv"
rows : list[list[Any]] = [[i, j] for i in range(5) for j in range(5)]
with open(csv_path, mode='w') as file:
    writer = csv.writer(file)
    writer.writer
if not issubclass(numbers.Integral, numbers.Rational):
    print("numbers.Integral must be a subclass of numbers.Rational")


# ── pathlib ──────────────────────────────────────────────────────────────────

path = pathlib.Path(__file__)
print(path.name)
print(path.parent)


# ── tempfile ─────────────────────────────────────────────────────────────────

path = tempfile.NamedTemporaryFile()
text = path.write_text("Hello world!")
print(text == "Hello world!")


