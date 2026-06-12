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

    def __repr__(self) -> str:
        n, u = divmod(self.reading, 1)
        m, s = divmod(n, 60)
        h, t = divmod(m, 60)
        return f'{h} hours {t:.3f}s'


# ── classmethod __new__, __init__, __call__ ──────────────────────────────────

class LazyInit(Generic[T]):
    def __init__(
        self,
        cls: type[T],
        *,
        init: Callable[P, T] = lambda _: None,
    ):
        self.cls = cls
        self.init  = init
        self.instance: Final[tuple[P, ...]] | None = None
        self.result:  Final[T]               | None = None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if self.instance is None:
            self.instance = args
            self.result   = self.cls(*args, **kwargs).result()
        return self.result


@LazyInit(float)
def lazy_float_factory(*args: P.args, **kwargs: P.kwargs) -> float:
    return sum(args or kwargs.values())

# ────────────────────────────────────────────────────────────────────────────


if __name__ == '__main__':
    
    # ── Main ──────────────────────────────────────────────────────────────────

    print("\nMain:")
    print("*" * 80)
    print()

    # ── TypedDict ──────────────────────────────────────────────────────────────

    print("TypedDict example:")
    user_record  = UserRecord(id=17942, name="John Doe", email="john@example.com", active=True, metadata={"plan": "premium"})
    metrics_record = MetricsRecord(latency_ms=1.234, throughput=10_000, error_rate=0.001)
    print(user_record)
    print(metrics_record)
    print()

    # ── Annotated constraints (runtime-checked via descriptor) ─────────────────

    print("Annotated constraints example:")
    sensor = Sensor(reading=-1.23, label="-1.23")
    print(sensor)
    sensor = Sensor(reading=1.23, label="1.23")
    print(sensor)
    print()

    # ─── classmethod __new__, __init        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
