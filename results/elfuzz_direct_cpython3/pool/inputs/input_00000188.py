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
    frame = sys._getframe()           # getstack() is not available before PyPy
    lst: list[str] = []
    while True:
        name = frame.f_code.co_name
        lst.append(name)

        next_frame = frame.f_back
        if next_frame is None:
            break
        frame = next_frame
    return reversed(lst)


def inspect_frames(frames: tuple[types.FrameType, ...]) -> None:
    """Print info on each frame, showing what's on top of the stack."""
    for idx, fr in enumerate(frames):
        print(f"\n=== Frame #{idx} ===")
        print(">> locals()")
        for key, value in fr.f_locals.items():
            print(f"{key}: {value}")
        print(">> globals()")
        for key, value in fr.f_globals.items():
            print(f"{key}: {value}")
        print(">> traceback.format_stack(fr)")
        traceback_lines = "".join(inspect.trace())
        print(traceback_lines)


# ── GC & Tracing ──────────────────────────────────────────────────────────────

def trace_gc_collections(collection_count: int, interval_ms: float) -> None:
    """Trace a given number of collection events.

    >>> trace_gc_collections(5, 0.2)

    """
    def callback(obj):
        pass
    tracer = tracemalloc.StartCallback(callback)
    gc.set_tracer(tracer)
    gc.collect()
    for _ in range(collection_count - 1):
        time.sleep(interval_ms / 1000.)
        gc.collect()


def gc_callback(obj: Any, reference_type: int | None) -> None:
    """Simple callback to show which objects are being collected.

    >>> gc.set_debug(gc.DEBUG_SAVEALL)
    >>> gc.enable()
    >>> gc.callbacks.append(gc_callback)
    >>> obj = [i for i in range(5)]
    >>> del obj
    """

    print((obj is None or type(obj).__name__, reference_type))


def gc_trace_all_objects(print_func: callable[[Any], None] | None = None) -> None:
    """Trace all live objects by default. Print them otherwise.

    >>> gc_trace_all_objects()

    """
    from itertools import count
    seen_ids: set[int] = set()
    for obj_id in count():
        try:
            obj = gc.get_referents(*gc.get_objects())[obj_id]
            if id(obj) in seen_ids:
                continue
            seen