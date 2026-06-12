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
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }

# ── GC stats ──────────────────────────────────────────────────────────────────

class TraceGc(object):
    def __init__(self, verbose=False) -> None:
        self.verbose = verbose
        self.start_gc()

    def start_gc(self) -> None:
        gc.disable()
        gc.set_debug(gc.DEBUG_SAVEALL | gc.DEBUG_STATS)

    def stop_gc(self) -> None:
        gc.enable()
        stats = gc.get_stats()
        print(f"GC stats:\n{stats}")
        print("=====")


# ── Tracing memory allocation ──────────────────────────────────────────────────

snapshot = tracemalloc.take_snapshot()

def allocate() -> None:
    # simulate allocation
    ctypes.c_int(42)

def print_top(snapshot, key_type='lineno', limit=10) -> None:
    snapshot = tracemalloc.take_snapshot(snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"))))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines:" % limit)
    for stat in top_stats[:limit]:
        print(stat)

    other = snapshot.filter_types('misc.other')
    print("{:.2f} MiB {} miscellaneous objects".format(
        other.bytes / 2**20, len(other)))

    line_count = sum(stat.count for stat in top_stats)
    print("%d total reference%s." % (line_count, "" if line_count == 1 else "s"))

print_top(tracemalloc.take_snapshot(), 'lineno')

# ── Weakrefs and slots ───────────────────────────────────────────────────────

def add_to_weakref_cache(obj: Any) -> None:
    weakref.ref(obj)

def create_instance(klass: type) -> object:
    klass().x

def use_slots(class_: type, instance: object) -> None:
    class_().__dict__["a"] = 5