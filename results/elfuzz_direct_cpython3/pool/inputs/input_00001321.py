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


class Temperature(Sensor):
    def __init__(self, label: str, reading: float):
        super().__init__(label, reading)


class Humidity(Sensor):
    def __init__(self, label: str, reading: float):
        super().__init__(label, reading)


# ── Never ───────────────────────────────────────────────────────────────────

class MyNeverType(Never[T]):  # type: ignore[type-arg]
    pass


# ── Annotated ────────────────────────────────────────────────────────────────

class SensorConfig(Annotated[_SensorConfig, _SensorConfig]):
    pass


class _SensorConfig:
    scale_factor: Annotated[int, positive, lambda v: v == 1] = _Constrained()


class TemperatureConfig(_SensorConfig):
    min_reading: Annotated[float, positive, lambda v: v < 30] = _Constrained()
    max_reading: Annotated[float, positive, lambda v: v > 90] = _Constrained()

    def __call__(self, sensor: Sensor) -> float:
        s: Temperature = sensor
        return self.scale_factor * (s.max_reading - s.min_reading) + s.min_reading


class HumidityConfig(_SensorConfig):
    min_reading: Annotated[float, positive, lambda v: v < 0.1] = _Constrained()
    max_reading: Annotated[float, positive, lambda v: v > 1]   = _Constrained()

    def __call__(self, sensor: Sensor) -> float:
        s: Humidity = sensor
        return self.scale_factor * (s.max_reading - s.min_reading) + s.min_reading


# ── get_type_hints ───────────────────────────────────────────────────────────

@staticmethod
def my_func(a: int, b: int = 100, /, c: str = "hi", d: str = "", e: str = "") -> str:
    """
    >>> from typing import cast
    >>> sig = get_type_hints(my_func)
    >>> cast(int, sig["a"])
    'int'
    >>> cast(str, sig["c"])
    'str'
    """

# ── reveal_type ──────────────────────────────────────────────────────────────

reveal_type("my_foo")


# ── TypedDict ─────────────────────────────────────────