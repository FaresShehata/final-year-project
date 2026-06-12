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
    runtime_checkable,
    Union,
    cast,
)


import logging
logging.basicConfig(level=logging.INFO)

# ── Asynchronous programming ──────────────────────────────────────────────────

async def my_coro():
    return 'Hello'


tasks = [
    asyncio.create_task(my_coro()),
    asyncio.create_task(my_coro()),
    asyncio.create_task(my_coro())
]

group = asyncio.gather(*tasks)
result = await group

# using task.cancel() and task.cancelled()

task = asyncio.create_task(my_coro())

try:
    result = await task
except asyncio.CancelledError:
    print(f"Task was cancelled at {time.perf_counter():.4} seconds")
finally:
    try:
        task.cancel()
    except asyncio.CancelledError:
        ...

# ── Async for ─────────────────────────────────────────────────────────────────

async def generator() -> list[int]:      # emulate an iterator
    yield from range(5)


async def main():
    async for item in generator():
        print(item)

loop = asyncio.new_event_loop()   # create a fresh event loop
loop.run_until_complete(main())   # run until completion
loop.close()                     # close it again after use
loop.run_forever()               #
loop.slow_callback_duration = 1000

# ── Async context managers ────────────────────────────────────────────────────

@asynccontextmanager
async def my_async_context_manager(value: str) -> AsyncIterator[str]:
    print(f'Entering my_async_context_manager("{value}")...')
    try:
        yield value
    finally:
        print(f'Leaving my_async_context_manager("{value}")...')

async with my_async_context_manager('hello') as value:
    assert value == 'hello'

async with my_async_context_manager('world') as value:
    assert value == 'world'


# ── Context manager transformation ───────────────────────────────────────────

async def adder(x: int, y: int) -> int:
    async with my_async_context_manager(x) as x_:
        async with my_async_context_manager(y) as y_:
            return x_ + y_

async def subtractor(x: int, y: int) -> int:
    async with my_async_context_manager(x) as x_, my_async_context_manager(y) as y_:
        return x_ - y_


# ── Async comprehensions ──────────────────────────────────────────────────────


import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
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


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    return types.FunctionType(new_co, fn.__globals__, name=new_name, argdefs=fn.__defaults__)


class MyFunction(types.FunctionType):

    @classmethod
    def replace(cls, *, defaults=None, closure=None, globals=None, qualname=None, name=None, doc=None, argcount=None,
                kwonlyargcount=None, nlocals=None, stacksize=None, code=None, consts=None, names=None, varnames=None,
                filename=None, name_location=None, firstlineno=None, lnotab=None, freevars=None, cellvars=None):
        raise NotImplementedError("This can only be done through object mutation")

    @property
    def qualname(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    class __bool__(types.FunctionType):     # type: ignore[misc]
        pass                                # TODO: test this out


my_function = MyFunction(
    fn.__code__,
    fn.__globals__,
    name='big_fun',
    argdefs=fn.__defaults__,
    closure=fn.__closure__,
    func_defaults=MyFunction.defaults(),
    )

# ── Ctypes ────────────────────────────────────────────────────────────────────


class FakeCStruct(ctypes.Structure):
    _fields_: tuple[tuple[str, Any], ...]


struct_type = FakeCStruct._asdict()
assert isinstance(struct_type['some_int'], int)

x = struct.pack('<i', 69)       # little-endian int
y = struct.unpack('<i', x)[0]

z = ctypes.c_uint32.from_buffer_copy(y)
assert z.value == y

ctypes.sizeof(FakeCStruct)
ctypes.addressof(z)
ctypes.alignment(FakeCStruct)

a = array.array('f', [1.0, 2.0])

array_repr = repr(a)
print(array_repr)
print(repr(array_repr))
print(textwrap.dedent(array_repr))

b = array.array('d', [1.0, 2.0])
c = array.array('d')
for v in b:
    c.append(v)

assert id(b) != id(c), 'Array instances must be independent'
assert len(b) == len(c), "Arrays have different lengths"
assert all([v == w for v, w in zip(b, c)]), "Arrays are not equal"

m = array.array('B', bytearray([69]))
n = array.array(m.typecode)
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
        if i % 2 == 0:               # this is the hot path
