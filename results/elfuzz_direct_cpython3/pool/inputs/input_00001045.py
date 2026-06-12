"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")


class A:
    """A class."""


class B(A):
    """B class."""


class C(B):
    """C class."""

    @classmethod
    def m(cls: type[C]) -> int:
        return len(cls.__mro__)

    def f(self: B, x: K) -> V:
        return self.__class__.__name__, "f", x

    def g(self: B, y: K) -> V:
        return self.__class__.__name__, "g", y


def get_mro(obj_or_cls) -> list[type]:
    cls = obj_or_cls if isinstance(obj_or_cls, type) else obj_or_cls.__class__
    if cls.__mro__ is not object.__mro__:
        return cls.__mro__
    return (object,) + (cls,)
get_mro.__annotations__ = {"obj_or_cls": type}


@dataclasses.dataclass
class SettledAwaitable(Generic[K]):
    key: K
    value: V | None = dataclasses.field(default=None)


async def main() -> None:
    c = C()
    await c.f("foo")
    await c.g("bar")
    assert c.m() == 3
    assert c.f("baz") == ("C", "f", "baz")
    assert c.g("qux") == ("C", "g", "qux")

    for i in range(4):
        await asyncio.sleep(.5)
        print(i)

    settled_results = [SettledAwaitable(key=i) for i in range(5)]
    for settled_result in settled_results:
        await settled_result
        print(settled_result.key, settled_result.value is None)

    settled_results = []
    for i in range(6):
        settled = SettledAwaitable(key=i)
        settled_results.append(asyncio.create_task(settled))
        await settled
        print(settled.key, settled.value is None)
    for task in settled_results:
        await task

    task = asyncio.create_task(c.f("foobar"))
    try:
        result = await task
        print(result)
    finally:
        await task


a = A()
b = B()
assert b in get_mro(b)
assert b in get_mro(a)
assert c in get_mro(c)
assert c in get_mro(b)
assert c in get_mro(a)
assert c not in get_mro(objectimport importlib.machinery
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

# ── dis - decodes bytecodes from a .pyc or .pyo file ──────────────────────────

PYTHON_BYTECODES = {
    'dis': dis.dis,
    'load_const': load_const,
    'load_name': load_name,
    'build_class': build_class,
}

for name, fn in PYTHON_BYTECODES.items():
    print(f"Disassembling {name}:")
    print(annotated_disassembly(fn))
    print()


# ── Code Objects ──────────────────────────────────────────────────────────────

SOURCE_CODE = textwrap.dedent("""
    def foo(x):
        x += 1
    del x
    """).strip()
print("\nCode object:")
CO = compile(SOURCE_CODE, filename="<demo>", mode="exec")

print(CO.co_filename)
print(CO.co_firstlineno)
print(CO.co_consts)
print(CO.co_names)
print(CO.co_varnames)

if CO.co_argcount == 0:
    print("No positional arguments.")
elif CO.co_argcount == 1:
    print("One positional argument:", CO.co_varnames[0])
else:
    raise Exception("Unexpected number of parameters.")

print(CO.co_kwonlyargcount)
print(CO.co_flags)

CO.func_code.co_freevars        # empty tuple
CO.func_code.co_cellvars         # empty tuple


# ── ctypes ────────────────────────────────────────────────────────────────────

def set_frame_locals(frame, names, values):
