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
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names[::-1]


def throw_exception() -> None:
    try:
        raise ValueError("oops")
    except Exception as exc:
        print(f"{exc=}")
        try:
            raise exc
        except Exception as inner_exc:
            print(f"{inner_exc=}")


def handle_broken_pipe(exc: BrokenPipeError) -> None:
    print(f"{exc.args=}")      # args includes errno and strerror
    print(f"{type(exc)=}")

# ── GC tracing ────────────────────────────────────────────────────────────────

def trace_gc(sleep_seconds: float = 1.5) -> None:
    """Iterate over the garbage collector's generation set at regular intervals.

    See also: trace_tracemalloc().
    """
    print("\nGC:")
    for gen_id in gc.get_objects():       # get all live objects
        obj = gc.garbage.get(gen_id, None)
        if obj is not None:
            print(obj)
    while True:
        time.sleep(sleep_seconds)
        print("\n\nNew GC:")
        for gen_id in gc.get_objects():
            obj = gc.garbage.get(gen_id, None)
            if obj is not None:
                print(obj)

# ── Tracing allocations ───────────────────────────────────────────────────────

def trace_tracemalloc(sleep_seconds: float = 1.5) -> None:
    """Trace the current heap usage at regular intervals.

    This uses the Python C API to hook into the allocation tracking system.
    """
    tracemalloc.start()
    try:
        print("\nTracelast:", tracemalloc.last()[:6])    # last snapshot
        while True:
            time.sleep(sleep_seconds)
            print("\n\nCurrent:", tracemalloc.tracemalloc_memory())
    finally:
        tracemalloc.stop()

# ── Weakrefs ──────────────────────────────────────────────────────────────────

class WeakRefInt(int):
    def __init__(self, value: int):
        super().__init__()     # default id() behavior

    def __repr__(self) -> str:
        return f"<{super().__repr__()} ({hex(id(self))})>"


def demo_weakref() -> None:
    wri = weakref.ref(WeakRefInt(1))
    assert isinstance(wri(), WeakRefInt)             # returns wrapped