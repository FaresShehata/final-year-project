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
    setattr(fn_new, "__module__", fn.__module__)   # pass original module back
    return (co_new, fn_new)


# ── CTypes ────────────────────────────────────────────────────────────────────

def c_short(value: int) -> ctypes.c_short:
    return ctypes.c_short(int(math.fabs(value)))


def c_int_8bit(value: int) -> ctypes.c_byte:
    return ctypes.c_byte(value)


def c_uint_8bit(value: int) -> ctypes.c_ubyte:
    return ctypes.c_ubyte(value)



# ── Struct ────────────────────────────────────────────────────────────────────

def pack_float(f: float) -> bytes:
    fmt = "f"
    size = struct.calcsize(fmt)
    raw_bytes = struct.pack(fmt, f)
    return raw_bytes[:size]


def unpack_float(raw: bytes) -> float:
    fmt = "f"
    size = struct.calcsize(fmt)
    value = struct.unpack_from(fmt, raw)[0]
    return value



# ── Arrays ────────────────────────────────────────────────────────────────────

def get_array_type(code: str) -> type[array.array]:
    """Get a suitable array type given a string like 'i' or 'f'."""
    # The following works only on Python 3.9+.
    # return eval(f"array.{code}")
    try:
        # This will work everywhere since 2022-06.
        return eval(f"array.{code.upper()}")     # noqa: ECE001
    except AttributeError as exc:
        raise ValueError(f"Unknown array type {code}") from exc


def test_arrays(arrays: list[type[array.ndarray]]) -> None:
    for dtype in ["u1", "b", "B"]:
        arr = array.array(dtype, [255])
        arr >>=        self.name = name
        self._age = age
    
    @property
    def age(self) -> int:
        return self._age
    
    
# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_person(person: Person, *, default=None) -> None:
    match person:
        case Person(name="Alice"):
            print("It's Alice!")
        case Person(age=30):
            print("They are 30 years old.")
        case Person():
            print("I don't know who this is.")
        case default:
            print(default)


# ── Walrus Operator ───────────────────────────────────────────────────────────

def find_index(lst: list[int], x: int) -> int:
    for i, v in enumerate(lst):
        if v == x:
            return i
    return -1


def find_index_walrus(lst: list[int], x: int) -> int:
    for i, v := enumerate(lst):
        if v == x:
            return i
    return -1


# ── Generics ───────────────────────────────────────────────────────────────────

class SortedList(G    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

