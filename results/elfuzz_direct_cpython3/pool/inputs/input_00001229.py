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

# ── dis - decodes bytecodes from a .pyc or .pyo file ──────────────────────────

PYTHON_BYTECODES = {
    'dis': dis.dis,
    'load_const': load_const,
    'load_name': load_name,
    'build_class': build_class,
}

for name, fn in PYTHON_BYTECODES.items():
    print(f"Disassembling {name}:")
    print(annotated_disassembly(fn))
    print()


# ── Code Objects ──────────────────────────────────────────────────────────────

SOURCE_CODE = textwrap.dedent("""
    def foo(x):
        x += 1
    del x
    """).strip()
print("\nCode object:")
CO = compile(SOURCE_CODE, filename="<demo>", mode="exec")

print(CO.co_filename)
print(CO.co_firstlineno)
print(CO.co_consts)
print(CO.co_names)
print(CO.co_varnames)

if CO.co_argcount == 0:
    print("No positional arguments.")
elif CO.co_argcount == 1:
    print("One positional argument:", CO.co_varnames[0])
else:
    print("Multiple positional arguments:")

args_spec = CO.co_argflags
for arg_idx in range(CO.co_argcount):
    if args_spec[arg_idx]:
        print("\t", CO.co_varnames[arg_idx])


# ── ctypes - allows you to create and manipulate C data structures ────────────

class IntArrayType(ctypes.Structure):
    _fields_ = [("value", ctypes.c_int)]


class IntArrayObject(ctypes.Structure):
    _fields_ = [
        ("ob_refcnt", ctypes.c_ssize_t),
        ("ob_type", ctypes.POINTER(IntArrayType)),
        ("items", ctypes.POINTER(IntArrayType)),
    ]


iarray = IntArrayObject()
ctypes.memset(iarray, 0x5a, ctypes.sizeof(IntArrayObject))

assert iarray.ob_type.contents.value == 0x5a
print(hex(iarray.__int__()))

# ── Struct - works with ctypes but is easier to use ───────────────────────────-

print("\nStruct:")
struct_format = "ii" # two integers of size 2 bytes each.
arr = struct.pack(struct_format, 3, 7)
print(arr)

struct_arr = struct.unpack(struct_format, arr)
print(struct_arr)


# ── Array ────────────────────────────────────────────────────────────────────

ARRAY_SIZES = [8*2**i for i in range(6)]

print("\nArrays:")
for size in ARRAY_SIZES:
    a = array.array('B', b"\xff"*size)
    print(a.itemsize, a.buffer_info(), len(a))


# ── MemoryView - wraps an existing buffer in Python's memory model ────────────

print("\nMemory views:")

data = b'\xff' * (20 * 1024 * 1024)
m = memoryview(data)
print(m.format, m.itemsize, m.shape, m.ndim, m.strides)

with open("test.txt", "w") as f:
    f.write(str(m))