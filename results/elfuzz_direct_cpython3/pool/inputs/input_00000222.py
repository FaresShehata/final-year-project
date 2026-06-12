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
    globs: dict = {}   # no globals needed here
    fn = compile(src, "<inline>", "exec")
    assert isinstance(fn, types.CodeType)

    # Create an empty FunctionType to build on top of using the compiled source above.
    fn_type = type(fn)
    # This is how you build a FunctionType without calling compile() again.
    new_fn = fn_type(fn.co_argcount, fn.co_nlocals, fn.co_stacksize, fn.co_flags, fn.co_code, fn.co_consts, fn.co_names, fn.co_varnames, fn.co_filename, fn.co_name, fn.co_firstlineno, fn.co_lnotab, fn.co_freevars, fn.co_cellvars, globs)
    return new_fn


def as_string(obj: Any) -> str:
    """Print object to string with repr(), but use __str__() when possible."""
    if hasattr(obj, "__str__"):
        return obj.__str__()
    elif hasattr(obj, "__repr__"):
        return repr(obj)
    else:
        raise TypeError(f"{obj} has neither __str__ nor __repr__")


# ── Ctypes and struct ─────────────────────────────────────────────────────────

class Complex(ctypes.Structure):
    _fields_ = [("r", ctypes.c_double), ("i", ctypes.c_double)]


complex_struct_size = ctypes.sizeof(Complex)


# ── Array module ──────────────────────────────────────────────────────────────

arr = array.array("B")
assert arr.typecode == "B"

arr.extend([x for x in range(256)])
assert all(arr[i] == i for i in range(len(arr)))

arr.append(127)
assert len(arr) == 257
assert all(x <= 127 for x in arr[:-1])
assert arr[-1] == 127


# ── Memory view ───────────────────────────────────────────────────────────────

mem_view = memoryview(arr)
assert mem_view.format == "B"
assert mem_view.itemsize == 1
assert len(mem_view) == len(arr)
for i in range(len(arr)):
    assert mem_view[i] == arr[i]

with pytest.raises(TypeError, match="memoryviews are read-only"):
    mem_view[3] = 99

new_mem_view = mem_view.cast("I")
assert not isinstance(new_mem_view, memoryview)
assert new_mem_view.itemsize == 4
assert new_mem_view