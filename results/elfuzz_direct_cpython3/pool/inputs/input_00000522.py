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
        if track["scope"] == "GC":
            print(f"{track['action']} at {track['start']:d} bytes")

    with tracemalloc.start():
        with tracemalloc.Context() as ctx:
            ctx.callbacks.register("GC", callback)

            # Run some operations that might trigger garbage collection
            gc.enable()
            del [i for i in range(10**6)]
            gc.disable()

    print(tracemalloc.take_snapshot())


# ── Weakrefs ─────────────────────────────────────────────────────────────────

def register_weakref_test() -> bool:
    """Register an arbitrary weak reference and unregister it after first use."""
    ref = weakref.ref(lambda x: print(x))
    result = True
    try:
        assert False, ref()
    except ReferenceError:
        result &= True
    finally:
        ref.clear()
        return result


def register_weakproxy_test() -> bool:
    """Register an arbitrary weak proxy and unregister it after first use."""
    class Foo:
        pass

    foo = Foo()
    ref = weakref.proxy(foo)
    result