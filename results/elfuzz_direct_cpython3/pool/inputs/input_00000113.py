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
    co_new = co.replace(co_name=new_name)
    fn_new = types.FunctionType(
        co_new,
        globals(),
        name=new_name,
        argcount=len(co.co_varnames),
        nlocals=len(co.co_cellvars),
        stacksize=co.co_stacksize,
        flags=co.co_flags,
        lnotab=co.co_lnotab.copy(),
        consts=list(co.co_consts),
        names=co.co_names,
        varnames=co.co_varnames,
        filename=co.co_filename,
        name=None,           # remove the original name from the cloned function
        freevars=tuple(),    # cloning does not create any free variables
        cellvars=co.co_cellvars,
    )
    setattr(fn_new, "__module__", fn.__module__)
    return fn_new


def clone_code_object(fn: types.FunctionType | None = None) -> tuple[types.CodeType, types.FunctionType]:
    """Clone the code object and add a new name to it."""
    co = getattr(fn or hot_path, '__code__', None)
    assert isinstance(co, types.CodeType)
    # The following line is equivalent to the two above lines.
    # co = co.clone(name='clone')       # not working on Python 3.7...
    # co = types.CodeType(*co.co_code, co.co_kwonlyargcount, co.co_nlocals, ...)
    co_new = co.replace(
        co_name="clone",
        filename=__file__,
    )
    fn_new = types.FunctionType(
        co_new,
        globals(),
        name="clone",
        argcount=co.co_argcount,
        nlocals=co.co_nlocals,
        stacksize=co.co_stacksize,
        flags=co.co_flags,
        lnotab=co.co_lnotab.copy(),
        consts=list(co.co_consts),
        names=co.co_names,
        varnames=co.co_varnames,
        filename=co.co_filename,
        name=None,   # remove the original name from the cloned function
        freevars=tuple(),
        cellvars=co.co_cellvars,
    )
    setattr(fn_new, "__module__", "seed.04")
    return co_new, fn_new


def replace_function_code_object(fn: types.FunctionType, new_code: bytes) -> types.FunctionType:
    """Replace the function code object by a new one."""
    co = fn.__code__
    assert isinstance(co,