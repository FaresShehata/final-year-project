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
    frame = sys._getframe()      # get caller's frame
    names: list[str] = []
    while frame is not None:
        name = frame.f_code.co_name
        if name != "<module>":   # ignore top-level module function
            names.append(name)
        frame = frame.f_back     # walk up to caller
    return names[::-1]


def frames_as_dict(frames: list[types.FrameType]) -> dict[int, types.FrameType]:
    """Convert frame list into dictionary keyed by frame ID."""
    return {id(frame): frame for frame in frames}


def find_frame(id_: int) -> types.FrameType | None:
    """Find frame by ID; returns None if not found."""
    for frame in sys._current_frames().values():
        if id(frame) == id_:
            return frame
    return None


# ── GC ────────────────────────────────────────────────────────────────────────

def run_garbage_collection() -> int:
    """Run garbage collection and return number of unreachable objects."""
    gc.collect()
    return len(gc.garbage)


# ── Tracing ───────────────────────────────────────────────────────────────────

def trace_gc_usage() -> None:
    """Trace garbage collection events using tracemalloc context manager."""
    def callback(_, current, previous, track):
        if track["scope"] == "GC":                 # scope of interest
            print(f"{track['usage']:.3f}GB was freed")

    with tracemalloc.StartSampling() as stats:     # start sampling
        gc.disable()                               # disable automatic collection
        # simulate large usage of heap, trigger GC runs
        run_garbage_collection() *= 100             # 100 times...
        # enable automatic collection again, but use our callback for tracing
        gc.enable()
        gc.set_tracing_callback(callback)

    # stop sampling, analyze result
    snapshot = stats.stop()
    # display top 5 statistics, sorted by decreasing size used since last GC
    stats.print_stats(sort="size", limit=5)


# ── Weakrefs ──────────────────────────────────────────────────────────────────

def create_weak_ref(obj: object) -> weakref.ref:
    ref = weakref.ref(obj)
    assert ref() == obj
    del obj                  # let reference go out-of-scope
    return ref               # still valid!


def create_weak_proxied(obj: object) -> weakref.proxy:
    proxied = create_weak_ref(obj)
    proxy = weakref.proxy(proxied)
    assert proxy() == obj
    del obj                  # let reference go out-of-scope
    return proxy             # still valid!


# ── Slots ─────────────────────────────────────────────────────────────────────

class Book:

    __slots__ = ("title", "_price")       # declare what slots are available

    def __init__(self, title, price) -> None:
        self.title = title
        self._price = price                # private attribute

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        self._price = value                # update public attribute


if __name__ == "__main__":
    # ── Bytecode introspection ──────────────────────────────────────────────────
    fn = annotated_disassembly(hot_path)
    print("Bytecode for hot path:")
    print(fn)
    print("-" * 60)
    print("Opcode counts:")
    print(count_opcodes(hot_path))
    # ──────────────────────────────────────────────────────────────────────────
    # ── Code object surgery ────────────────────────────────────────────────────
    code_object = annotate_hot_path(h