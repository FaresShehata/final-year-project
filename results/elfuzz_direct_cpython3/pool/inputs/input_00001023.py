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
T2                     = TypeVar("T2")
R                     = TypeVar("R")

Constraint: TypeAlias = Callable[[T1, T2], bool]
Constraints: TypeAlias = tuple[Constraint[T1, T2], ...]

ParamSpecKwarg: TypeAlias = ParamSpec[Kwargs]


# ── Class & method decorator examples ─────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exc_types) -> ContextManager[None]:
    try:
        yield
    except exc_types:
        pass


# ── Context manager with an inner class ───────────────────────────────────────

class FileDeleter(contextlib.AbstractContextManager):
    class TempFile:
        def __init__(self, path):
            self.path = path

        def __enter__(self):
            print(f'Creating {self.path}')
            self.file = fileio.TempFile.create(path=self.path)
            return self.file

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                print(f'Deleting {self.path}')
                os.remove(self.path)


# ── Decorator example (which returns a function) ──────────────────────────────

def trace(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        elapsed_time = end_time - start_time
        print(f'{func.__name__}{args}() took {elapsed_time:.6f}s')

        return result

    return wrapper


# ── multiprocessing.Pool.map() vs pool.imap_unordered() ───────────────────────

source = [i for i in itertools.count(start=1)]

pool_map = multiprocessing.Pool().map
pool_imap = multiprocessing.Pool().imap_unordered

print(pool_map(len, source))      # [len(source)] (sequential)
print(list(pool_imap(len, source)))  # [0,..., len(source)-1] (parallel)

# ───────────────────────────────────────────────────────────────────────────────

# ── How many times does the following loop execute? ───────────────────────────

for i in range(10**12):
    pass

# Answer: it aborts after approximately 2^31 iterations.

# ─────────────────    return buf.getvalue()


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
            total -= i * i
    return total


print(annotated_disassembly(hot_path))
print(count_opcodes(hot_path))

# ───────────────────────────────────────────────────────────────────────────────

# ── Dis ────────────────────────────────────────────────────────────────────────

target_pyc = "seed_04.pyc"

with open(target_pyc, 'wb') as f:
    f.write(b'\x03\x00\x00\x00\x05\x00\x00\x00\xf7\x00\x00\x00')
    f.write(struct.pack('h', -18))

dis.disassemble(target_pyc)

# ───────────────────────────────────────────────────────────────────────────────

# ── Code object representation ────────────────────────────────────────────────

CODE_OBJ_SIZE = 96   # for CPython 3.9.7

raw_code_obj = b"\x03" \
               b"\x00" \
               b"\x00" \
               b"\x00" \
               b"\xff\xff\xff\xff" \
               b"\xff\xff\xff\xff" \
               b"\xff\xff\xff\xff" \
               b"\xff\xff\xff\xff" \
               b"\xfe" \
               b"\xff" \
               b"\xf0" \
               b"\xff" \
               b"\xff" \
               b"\xf1" \
               b"\xff" \
               b"\xf2" \
               b"\xff" \
               b"\xf3" \
               b"\xff" \
               b"\xf4" \
               b"\xff" \
               b"\xf5" \
               b"\xff" \
               b"\xf6" \
               b"\xff" \
               b"\xf7" \
               b"\xff" \
               b"\xf8" \
               b"\xff" \
               b"\xf9" \
               b"\xff" \
               b"\xfa" \
               b"\xff" \
               b"\xfb" \
               b"\xff" \
               b"\xfc" \
               b"\xff" \
               b"\xfd" \
               b"\xff" \
               b"\xfe" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
