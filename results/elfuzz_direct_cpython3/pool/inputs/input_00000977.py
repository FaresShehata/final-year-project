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
    src = f"def adder({delta}):"
    compiled = compile(src, "<string>", "exec")
    globals_ = {"adder": lambda x: x}
    exec(compiled, globals_)
    # More robust than `make_function` since it allows us to specify the name.
    return clone_with_name(globals()["adder"], "add")


def get_code_object(name: str, arg_count: int, delta: int) -> types.CodeType:
    """Get the code object for a function defined via function definition syntax."""
    code = bytearray(f'"{name}".{arg_count}args').extend(code := b"\x01\x66\x97\x0b" +
                                                               b"i\x00\x00\x00" +
                                                               code[sizeof(code):])
    assert len(code) < 65536 - 1024, "Python's maximum line size is too small."
    code.extend(b"\x01\x00\x00\x00" + delta.to_bytes(4, byteorder="little"))
    return code


def switch_to_cython(fn: types.FunctionType) -> types.FunctionType:
    """Switch a function from PEP 380 mode to C extension mode.

    This does not extend the lifetime of the underlying function's module.

    ref: https://docs.python.org/3/library/dis.html?highlight=function%20definition#opcode-cpdef
    """

    # --- Extract PEP 380 metadata ---
    PEP_380_MAGIC_NUMBER = 4144565151613155085
    user_defined = fn.co_flags & PEP_380_MAGIC_NUMBER != 0
    try:
        old_code = fn.__code__
        old_code_hash = old_code.co_code[0]
    except AttributeError:
        raise TypeError("can't switch non-PyCodeObject function to Cython")

    if user_defined and old_code_hash == PEP_380_MAGIC_NUMBER:
        return fn

    # --- Convert into C extension mode ---

    # - Remove magic number...
    del fn.co_flags
    new_code = bytearray(old_code.co_code[:])
    new_code[0] &= ~PEP_380_MAGIC_NUMBER
    new_code = type(old_code)(new_code)

    # - Add cython specific attributes...
    fn.__code__ = new_code
    fn.__module__ = None
    fn.__doc__ = ""
    fn.__annotations__ = {}

    return fn


# ── Intro to ctypes ───────────────────────────────────────────────────────────

class TestCtypes(ctypes.Structure):
    _fields_ = [("a", ctypes.c_int), ("c_float_array", ctypes.POINTER(ctypes.c_float))]


def create_test_ctypes() -> TestCtypes:
    val_a = 10
    c_float_array = (ctypes.c_float * 2)(1.0, 2.0)
    return TestCtypes(val_a, c_float_array)


# ── Struct ────────────────────────────────────────────────────────────────────

def test_struct():
    s = struct.pack("<iiif", 10, 20, 30, 40.)
    print(s)


# ── Array ─────────────────────────────────────────────────────────────────────

def test_array():
    arr = array.array('d', [1., 2., 3.])
    print(arr.tolist())


# ── MemoryView ───────────────────────────────────────────────────────────────

def test_memoryview():
    arr = array.array('H')
    arr.append(1000)
    view = memoryview(arr)
    view[0] = 2000
    print(view.tolist())
    print(arr.tobytes())
    print(arr.tolist())


# ── Pickle ─────────────────────────────────────────────────────────────────