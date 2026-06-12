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
# https://docs.python.org/3/library/dis.html
def foo() -> None:
    print("Hello world!")


print(dis.dis(foo))

# ── Dis │ Instruction name | Opcode | Operand type | Operand
dis.show_code(foo)

# ── Code objects ──────────────────────────────────────────────────────────────
foo_code = foo.__code__

for attr in dir(foo_code):
    print(attr)
    if not callable(getattr(foo_code, attr)):
        print(f"  {getattr(foo_code, attr)}")

print(foo_code.co_filename)

# ── Ctypes ────────────────────────────────────────────────────────────────────
class TestStruct(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_char * 256)]

test_struct = TestStruct()
assert test_struct.x == 0
assert test_struct.y == b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
test_struct._fields_[1][1] = "TEST".encode()
assert (
    test_struct.y.decode() == "TE\0ST\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"
)
assert test_struct.y == b"TE\0ST\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"

# ── Struct and array ──────────────────────────────────────────────────────────
struct_test = struct.pack("<I", 0xDEADBEEF)
array_test = array.array("B", [0xE, 0xD, 0xA, 0xB, 0xF])
print(struct_test.hex())
assert struct.unpack("<I", struct_test)[0] == 0xDEADBEEF
assert array_test[0] == 0xE and array_test[-1] == 0xF

# ── Memory view ──────────────────────────────────────────────────────────────
#
mem_view = memory