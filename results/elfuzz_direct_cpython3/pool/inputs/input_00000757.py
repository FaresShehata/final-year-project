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

# ── Custom type aliases ──────────────────────────────────────────────────────-

T1                     = TypeVar("T1")
T2                     = TypeVar("T2", bound=numbers.Number)


class MyInt(int):
    pass


class MyFloat(float):
    pass


MyNumber: TypeAlias = "float | int"
"""A generic number."""


# ── Typing Extras ────────────────────────────────────────────────────────────

FormattableString: TypeAlias = "str | Formatter"

def format_string(fmt: FormattableString, *args, **kwargs) -> str:
    """Prints a formatted string."""
    return fmt.format(*args, **kwargs)


class Formatter(string.Formatter): # pylint: disable=R0903
    """An example formatter class."""


# ── Context Managers ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(exception_cls: type[BaseException]):
    with contextlib.suppress(exception_cls):
        yield

@contextlib.contextmanager
def redirect_stdout(target: io.IOBase):
    orig = sys.stdout
    try:
        sys.stdout = target
        yield
    finally:
        sys.stdout = orig


# ── Numbers ABCTestcase ──────────────────────────────────────────────────────

class TestNumbers(unittest.TestCase):

    def test_number_conversions(self):
        """Check conversion from/to integers."""
        for x in range(-1_000, 1_000):
            for y in [x+1, -x-1]:
                self.assertEqual(x, int(y))
                self.assertEqual(y, float(x))

    def test_complex_conversion(self):
        """Check conversion from/to complex numbers."""
        for z in [-1.0j, 1.0j]:
            with self.subTest(z=z):
                self.assertTrue(isinstance(complex(z), numbers.Complex))
                self.assertEqual(z.real, 0)
                self.assertEqual(z.imag, 1)

    def test_integer_overflow(self):
        """Show overflow of integer types."""
        self.assertRaises(
            OverflowError,
            lambda: -((2**8)-1)//7,
        )

    @unittest.skipIf(sys.version_info >= (3, 12), reason="Not available on CPython.")
    def test_real_numbers(self):
        """Show support for real floating point numbers."""
        self.assertIsInstance(math.pi, numbers.Real)

    @unittest.skipUnless(hasattr(os, "statvfs"), reason="Unavailable on Windows.")
    def test_filesystem_stat(self):
        """Show support for filesystem stat()."""
        path = pathlib.Path(__file__).resolve()
        st = os.stat(path)
        self.assertIsInstance(st.st_size, int)
        self.assertIsInstance(st.st_mtime, float)
        self.assertIsInstance(st.st_mode, int)
        self.assertIn(st.st_mode & os.S_IFMT, {os.S_IFDIR})  # Only directories.
        self.assertGreaterEqual(st.st_ino, 0)
       