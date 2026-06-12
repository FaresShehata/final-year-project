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
assert test_struct.y == b""


# ── Struct │ pack, unpack, calcsize
struct.pack("<i", 1)  # little endian int (4 bytes)
struct.pack(">f", 1.0)  # big endian float (4 bytes)
struct.pack("!Ih", 1, 2)  # ! — endianness; I — unsigned int; h — signed short
struct.unpack("<i", b"\x01\x00\x00\x00")  # little-endian int (4 bytes)
struct.calcsize("!II")  # calculate size of two unsigned ints

# ── Array │ array.array('d', [0, 1])
array.array("d", [0, 1])

# ── MemoryView │ m = memoryview(b'ABC')
m = memoryview(b"ABC")
m.cast("c")  # cast to char
m[0] = ord("X")  # replace first byte with X
m.tobytes()  # convert to bytes object

# ── Pickle │ Pickle
with open("/Users/fredrikpalmen/data/test.pickle", "rb") as f:
    print(pickle.load(f))

pickle.dumps(128 + 77j)
pickle.dumps(["a", {"b": 2}, 3])
pickle.dumps({"foo": ["bar", 1], "baz": b"quux"})
pickle.dumps(tuple(range(10)))
pickle.loads(b'\x80\x04\x95\xc2\x03\x00\x00\x00\x00\x00\x00\x00]\x93.'
             b'\x0c(\x8c\x03spam\x94)\x8c\x01egg\x94S.')
pickle.dumps((None, (), [], {}, set(), b"", bytearray()))
pickle.dumps([range(10)])
pickle.dumps(lambda x: x ** 2)  # TypeError: a 'lambda' is not JSON serializable
pickle.dumps(sys.modules[__name__].__loader__)  # AttributeError: module 'sys' has no attribute '__loader__'
pickle.dumps(sys.path)

# ── CopyReg │ copy_reg
copy_reg.pickle(dict, dict.copy)  # register custom pickling function for dictionaries
copy_reg.dispatch_table[id(dict)] = dict.copy  # override default