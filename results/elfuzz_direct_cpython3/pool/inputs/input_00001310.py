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
print(annotated_disassembly(lambda x: x + 1))

def show_bytecode(func):
    print(dis.Bytecode(func))
show_bytecode(lambda x: x ** 2)

for op in dis.opmap.values():
    print(f"{op}:\t{dis.opname[op]}")

def generate_code(a: int | None = None, b: float = 3.5):
    if a is not None and b < 2.7:
        raise ValueError("b must be >= 2.7")

    return (a * b).to_bytes(length=9, byteorder=sys.byteorder, signed=True)

print(generate_code.__code__.co_varnames)
print(generate_code.__code__.co_freevars)
print(generate_code.__code__.co_cellvars)

# ── Code Objects ──────────────────────────────────────────────────────────────

# The 'code' type represents the Python bytecode of a function or method.
c = compile(
    "y = 5",
    filename="func.py",
    mode='exec',
    dont_inherit=True
)
print(c.co_stacksize)
print(c.co_flags & 0x80 == 0x80)
print(c.co_names)
print(c.co_consts[0].startswith('lambda'))

f = c.func_code
print(type(f))

class MyFunctionCode(types.CodeType):
    def func(self):
        return self.co_filename.replace('.py', '.txt')

print(MyFunctionCode.from_code(f).func())

d = f.co_consts[0]
if isinstance(d, types.FunctionType):
    d() # TypeError: 'NoneType' object is not callable

# A 'function' type can only contain one code object
assert len(function.__code__) > 1

# The 'method' type contains two code objects
m = function.__call__.__func__
assert m.__code__.co_argcount == 1
assert m.__self__.func_code.co_argcount == 1

# Class methods are stored as closures
cm = classmethod(m)
assert cm.__code__.co_argcount == 1
assert cm.__closure__[0].cell_contents == m

# Static methods are stored as functions
sm = staticmethod(m)
assert sm.__code__ == m.__code__

# ── Struct ────────────────────────────────────────────────────────────────────

print(struct.calcsize("<i")) # little-endian
print(struct.pack('<i', 123456789101112131415))

s = struct.Struct(">ih")
p = s.pack_into(io.BytesIO(), 0, 123, 456)
print(s.unpack(p))
print(s.unpack_from(io.BytesIO(p)))
assert p == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

# ── Array ────────────────────────────────────────────────────────────────────

arr = array.array('B')
arr.append(1)
arr.extend((2, 3))
arr.insert(0, 0)
arr.pop(3)
arr.remove(2)
arr.reverse()

del arr[1]


# ── Memoryview ────────────────────────────────────────────────────────────────


mv = memoryview(arr.buffer_info()[0])
mv.readonly = True
mv.cast('I')[0] = 1
print(mv.tobytes())


# ── Pickle ────────────────────────────────────────────────────────────────────

pickle.dumps([0, 1, 2], protocol=pickle.HIGHEST_PROTOCOL)
pickle.loads(b"\\x80\\x04\\x95R\\x00\\x00\\x00\\x00\\x00\\x00\\x00--|")

data = pickle.dumps(object())
print(data.startswith(pickle.PICKLE_PREFIX))
print(data.endswith(pickle.PICKLE_EOF))


# ─
# ── Ctypes ────────────────────────────────────────────────────────────────────

print(ctypes.sizeof(ctypes.c_void_p)) # size of pointer on the current platform
print(ctypes.sizeof(ctypes.c_longdouble)) # size of long double on the current platfrom
ctypes.c_double(-2**63-1).value
ctypes.c_int(2**31 - 1).value
ctypes.c_uint(2**32).value
ctypes.c_char(b'A').value
ctypes.c_wchar(u'\u2603') # Unicode character for Christmas tree emoji
ctypes.c_ubyte(255).value