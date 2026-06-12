"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

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
    return types.FunctionType(new_co, fn.__globals__, name=new_name, argcount=fn.__code__.co_argcount)

def strip_none(fn: types.FunctionType) -> types.FunctionType:
    """Return a copy of fn where each argument is stripped from None."""
    args = list(inspect.signature(fn).parameters.values())
    params_to_strip = [p for p in args if p.default is None]
    sig = inspect.Signature(
        parameters=[p.replace(default=None) for p in args],
        return_annotation=args[-1].default if len(args) > 1 else None
    )
    return types.FunctionType(sig.bind(*[None]*len(params_to_strip), **{k:p.name for k,p in enumerate(params_to_strip)}).args, fn.__globals__)

@strip_none
def add(a: int, b: int) -> int: ...      # signature of `a+b` without `a=b`
assert add(1, 2) == 3

add = clone_with_name(strip_none(add), 'add')     # type `a=a+1`
print(add.__name__)                               # output: add

hot_add = hot_path(add)
print(hot_add(1, 2))                              # output: 3




# ─── Object-oriented programming ─────────────────────────────────────────────

class FooBar(object):                     # Python 2.x or the old-style class
    def __init__(self, x: int, y: float) -> None:
        self._x = x
        self.y = y

    @property
    def x(self) -> int:
        return self._x

    def double_x(self) -> None:
        self._x *= 2

foo_bar = FooBar(x=69, y=.5)
print(foo_bar.x)                          # output: 69
print(foo_bar.y)                          # output: 0.5
foo_bar.double_x()
print(foo_bar.x)                          # output: 138



class FooBarClass:                        # Python 3.7+
    def __init__(self, x: int, y: float) -> None:
        self._x = x
        self.y = y

    @property
    def x(self) -> int:
        return self._x

    def double_x(self) -> None:
        self._x *= 2

foo_bar_class = FooBarClass(x=69,
urls = ["https://example.com/page-1.html",
        "https://example.com/page-2.html"]

for url in urls:
    body = await fetch(url=url)
try:
    try:
        raise ValueError('This is an exception')
<|file_sep|><|fim_prefix|>/python/seed_06.py
#!/usr/bin/env python3
"""Nursery Examples

Examples to show basic functionality and syntax of the nursery.
"""

from __future__ import annotations

import gc

from nursery import Nursery, nurseryify


@nurseryify
async def run():
    async with Nursery(max_nursery_size=1) as nursery:
        asyncio.create_task(yield_from_func(), nursery=nursery)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
    loop.close()

    gc.collect()



from __future__ import annotations

import gc

from nursery import Nursery, nurseryify


@nurseryify
async def run():
    async with Nursery(max_nursery_size=1) as nursery:
        await asyncio.gather(
            asyncio.create_task(asyncio.sleep(1)),
            yield_from_func(),
            asyncio.create_task(asyncio.sleep(1))
        )


if __name__ == '__main__':
    import asyncio

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
    loop.close()

    gc.collect()



from __future__ import annotations

import gc

from nursery import Nursery, nurseryify


@nurseryify
async def run():
    async with Nursery(max_nursery_size=1) as nursery:
        await asyncio.gather(
            asyncio.create_task(asyncio.sleep(1),
                                nursery=nursery),
            yield_from_func(),
            asyncio.create_task(asyncio.sleep(1),
                                nursery=nursery)
        )


if __name__ == '__main__':
    import asyncio

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
    loop.close()

    gc.collect()



from __future__ import annotations

import gc

from nursery import Nursery, nurseryify


@nurseryify
async def run():
    async with Nursery(max_nursery_size=1) as nursery:
        await asyncio.gather(
            asyncio.create_task(asyncio.sleep(1)),
            asyncio.create_task(yield_from_func(),
                                nursery=nursery),
            asyncio.create_task(asyncio.sleep(1),
                                nursery=nursery)
        )


if __name__ == '__main__':
    import asyncio

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())
    loop.close()

    gc.collect()



from __future__ import annotations

import gc

except OSError as e:
    print(e)
else:
    print("The file was found.")



