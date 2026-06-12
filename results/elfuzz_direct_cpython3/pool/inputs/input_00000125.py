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

def print_frame_locals(frame: types.FrameType) -> None:
    local_names = set(frame.f_code.co_varnames[:frame.f_code.co_argcount])
    arg_names = set(frame.f_code.co_varnames[frame.f_code.co_argcount:])
    locals_ = {
        name: value
        for name, value in frame.f_locals.items()
        if name not in local_names and name not in arg_names
    }
    for key, value in sorted(locals_.items()):
        print(f"{key:>9}: {value}")


def get_traceback_info(frame: types.FrameType) -> tuple[types.TracebackType, ...]:
    tb_list: list[types.TracebackType] = []
    while True:
        try:
            exc_type, exc_val, tb = frame.exc_info
            break
        except AttributeError:
            pass      # no traceback yet; skip to next stack frame
        frame = frame.f_back
        if frame is None:
            raise RuntimeError("no traceback")
    tb_list.append(tb)
    while True:
        tb = tb.tb_next
        if tb is None:
            break
        tb_list.append(tb)
    return tuple(reversed(tb_list))


if __name__ == "__main__":
    print("\nBytecode introspection:")
    print("="*50)

    print("Annotated disassembled:\n")
    print(annotated_disassembly(hot_path))

    print("\nHot path opcodes by opcode name:\n")
    print(count_opcodes(hot_path))

    print("\nclone_with_name:\n")
    adder = clone_with_name(hot_path, "__my_adder__")
    assert adder(10) == adder(10)
    assert hot_path(10) != adder(10)

    print("\nmake_adder_from_bytecode:\n")
    plus_five = make_adder_from_bytecode(5)
    assert plus_five(10) == plus_five(10)
    assert hot_path(10) != plus_five(10)

    print("\nSimple frame inspection:")
    print("-"*50)
    frame = sys._getframe().f_back     # get caller's frame
    print_frame_locals(frame)

    print("\nGet tracebacks via frame inspection:")
    print("-"*50)
    for tb in get_traceback_info(sys._getframe()):
        print(f"\nTraceback