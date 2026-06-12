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


class MyStr(str):
    pass


MyTypeVar1             = TypeVar("MyTypeVar1", int, MyInt)
MyTypeVar2             = TypeVar("MyTypeVar2", float, MyFloat, MyComplex)
MyGenericClass         = TypeVar("MyGenericClass", bound="MyGeneric")


class MyGeneric(Generic[T]):
    ...


class MyStruct(NamedTuple):
    x: float
    y: Complex = field(default_factory=lambda: complex())


# ── PathLib helpers ─────────────────────────────────────────────────────────

with tempfile.TemporaryDirectory() as tmpdirname:
    path    = pathlib.Path(tmpdirname + "/abc/xyz.txt")
    parent  = path.parent
    stem    = path.stem
    suffix  = path.suffix
    basename= path.name
    dirname = path.dirname
    filename= path.filename
    absolute= path.absolute()
    relative_to= path.relative_to(pathlib.Path(tmpdirname))
    exists=(path.exists() or True)
    expanduser=path.expanduser()

for p in pathlib.Path.cwd().iterdir():
    print(p)

for i in range(3):
    print((i % 4).text_wrap())

for c in reversed(string.ascii_lowercase):
    print(c.text_wrap())

print(textwrap.dedent(r'''
    A literal block with raw HTML markup in it.
'''))

print(repr(ast.parse('foo')))

print(list(itertools.zip_longest(*[str(n).zfill(2) for n in range(15)])))

print(UserRecord(id=1, name='Alice', email='alice@example.com'))

print(MetricsRecord(latency_ms=.1))

print(MyGeneric[int](x=2, y=3.0))

print(((1+3j)*2-4)/(-8)**.3)

print(my_int_user_record := UserRecord(id=1, name='Alice', email='alice@example.com'))
print(user_records := [my_int_user_record])

print(UserRecord(x=10, y=20)) # Error

print(MyInt(12))
print(MyFloat(.1e-5))

print(MyStr('hello world'))

print(MyGeneric[float](x=1, y=2))

print(MyStruct(x=-1.23, y=complex()))

if False:
    print()

try:
    print(MyStruct(x=1, z=2)) # Error
except TypeError as e:
    print(e)

tup             @contextlib.contextmanager
def redirect_stdout(out: io.StringIO):
    old = sys.stdout
    sys.stdout = out
    try:
        yield
    finally:
        sys.stdout = old


# ── Numbers ABIs ────────────────────────────────────────────────────────────

default_float_info = {
    "Emax": 709,
    "emin": -708,
}


def make_default_float_info(**overrides: int) -> dict[str, int]:
    """Make a copy of default_float_info with overrides."""
    info = {**default_float_info}
    info.update(overrides)
    return info


class FloatInfo(numbers.FloatInfo):
    def __new__(cls, **kwargs):
        return super().__new__(cls, make_default_float_info(**kwargs))


class PositiveFloatInfo(FloatInfo):
    Emax: int
    emin: int
