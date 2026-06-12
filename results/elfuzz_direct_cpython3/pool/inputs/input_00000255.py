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


def get_function_call_stack() -> list[types.FrameType]:
    """Get all frames on our call stack by walking the traceback."""
    tb = sys.exc_info()[2]
    frames: list[types.FrameType] = []
    while tb is not None:
        frame = tb.tb_frame
        if frame is not None:
            frames.append(frame)
        tb = tb.tb_next
    return frames


def print_stack_depth(stack: list[types.FrameType]) -> None:
    """Print out a table showing each frame's depth, name, and locals."""
    widths = [max(len(name) or "", len(str(loc))) for loc in zip(*stack)]
    format_str = ("|%%-%ds | %%-30s | " + "%-" + str(width - 6) + "s") * len(stack[-1].f_locals)
    max_len = sum(widths) + len(format_str) - 1
    sep = "+%s+" % "+" + "-".join(["-" * w for w in widths])
    print(sep)
    print("|   %-7s |     %-30s | %-" + str(max_len - 9) + "s")
    print(sep)
    print(format_str % tuple(("Depth", "Name", "Locals")))
    print(sep)
    for frame in reversed(stack):
        print(" ".join([f"{n:<{w}}" for n, w in zip((len(stack) - idx, frame.f_code.co_name, repr(frame.f_locals)), widths)]))


# ── GC tracing ────────────────────────────────────────────────────────────────

def trace_reachable(obj: Any) -> set[Any]:
    reachable: set[Any] = set()
    seen: set[Any] = set()

    def explore(o: Any) -> None:
        if isinstance(o, (list, tuple)):
            for e in o:
                explore(e)
        elif isinstance(o, dict):
            for k in o.keys():
                explore(k)
            for v in o.values():
                explore(v)
        elif id(o) not in seen:
            seen.add(id(o))
            reachable.add(o)

    explore(obj)
    return reachable


# ── Tracing allocation history ────────────────────────────────────────────────

@tracemalloc.TimedSection
def allocate_objects(num: int) -> None:
    for _ in range(num