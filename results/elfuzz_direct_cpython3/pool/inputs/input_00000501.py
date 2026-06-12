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

    constraint: tuple[Any, ...]
    args:       tuple[int, int]

    def __init__(self, annotation: type[_Constrained], *args: Any, **kwargs: Any) -> None:
        self.constraint = kwargs.pop("_constraint", ())
        self.args = args
        super().__init__(annotation, *args, **kwargs)

    @property
    def _name(self) -> str:
        return str(type(self)).split("'")[1].split(".")[-1]

    def __get__(self, obj: Any, cls: type[Any]) -> Any:
        result = getattr(obj, "_" + self._name, None)
        if result is None:
            raise AttributeError(
                f"No such attribute '{self._name}' "
                f"in instance of type {type(cls).__qualname__}",
            )
        return result

    def __set__(self, obj: Any, value: Any) -> None:
        expected_types = [t.__origin__ for t in self.constraint]
        fail_msg = (
            f"'{value}' ({type(value)}) does not match one of the following types: "
            + ", ".join([t.__name__ for t in expected_types])
        )

        if any(isinstance(value, tp) for tp in expected_types):
            setattr(obj, "_" + self._name, value)
            return

        raise TypeError(fail_msg)

    def __repr__(self) -> str:
        return repr(getattr(self, "_name")) + "." + super().__repr__()



@Annotated[
    _Constrained[int, int],
    "This value must be an integer between 1 and 10",
]
def constrained_function(x: int) -> None:
    pass



# ── ParamSpec ─────────────────────────────────────────────────────────────────

ParamSpec1: TypeAlias = ParamSpec["ParamSpec1"]
ParamSpec2: TypeAlias = ParamSpec["ParamSpec2"]


def foo(*a: ParamSpec1, **kw: ParamSpec2) -> None:
    ...


foo(1, x="abc", y=2.5)
foo(1, 2, 3, {"x": "y"})  # Error!


# ── Concatenate ───────────────────────────────────────────────────────────────

Concatenate[T, Tuple[X]]: TypeAlias = T | Tuple[X]


Concatenate[str, Tuple[int]]: str
Concatenate["hello world", Tupleimport types
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
    for _ in range(2 ** n):
        total += 1 + (total * total - 3) // 5 + (-8 if total else 0) + 7
    return total


def main() -> None:
    print("\nBytecode introspection\n")
    print(f"{annotated_disassembly(hot_path)}")
    print(count_opcodes(hot_path))


if __name__ == "__main__":
    main()

# ───────────────────────────────────────────────────────────────────────────────

# ── Dis ────────────────────────────────────────────────────────────────────────

print("\nDis assembly of a function\n")


class MyInt(int):

    def __init__(self, value: int | str) -> None:
        super().__init__()
        self.value = int(value)


def func(myint: MyInt) -> str:

    my_int = MyInt("test")

    s: str = "Hello World!"[:myint]

    return f"Result is {s}"


print(dis.dis(func))


# ───────────────────────────────────────────────────────────────────────────────

# ── Code object ────────────────────────────────────────────────────────────────

print("\nCode object used by a function\n")


class MyInt(int):

    def __init__(self, value: int | str) -> None:
        super().__init__()
        self.value = int(value)


def func(myint: MyInt) -> str:

    my_int = MyInt("test")

    s: str = "Hello World!"

    return f"Result is {s[0:myint]}"

f_code = func.__code__

print("Function name:", f_code.co_name)
print("Source file name:", f_code.co_filename)

if isinstance(f_code.co_consts, list):
    const_iter = iter(f_code.co_consts)
else:
    const_iter = iter(list(f_code.co_consts))

for i, item in enumerate(const_iter, start=1):
    print(f"Constant {i}: {item}")

# ───────────────────────────────────────────────────────────────────────────────

# ── Ctypes ────────────────────────────────────────────────────────────────────

print("\nCtypes example with class\n")


class MyClass(ctypes.c_uint64):

    _id = 1

    def __new__(cls, value: int | str) ->