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
    print("Positional arguments:", ", ".join(CO.co_varnames[:CO.co_argcount]))

print(CO.co_code)
print(dis.code_info(CO.co_code))


# ── Ctypes ───────────────────────────────────────────────────────────────────

class MyStruct(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_float),
        ("z", ctypes.c_double),
    ]

struct = MyStruct()
struct.x = 25
struct.y = 36.7
struct.z = 98.7e-23

print(struct.__sizeof__())
print(struct.x, struct.y, struct.z)


# ── Struct ───────────────────────────────────────────────────────────────────-

array.array('i', [1, 2, 3]).tostring()
bytes([1, 3, 4])
bytes(range(1, 6)) + b'!'
b'CDEFGHI'


# ── Array ───────────────────────────────────────────────────────────────────-

a = array.array('d')
a.append(float('nan'))
print(a.tolist()) # nan is represented as the string "Nan"

# ── MemoryView ───────────────────────────────────────────────────────────────

memv = memoryview(b'ABCDEFGH')
print(memv.tolist())

# ── Pickle ───────────────────────────────────────────────────────────────────

data = {'a': (1,), 'tuple': ('hello', 'world'), 'list': ['hi', 'there']}
s = pickle.dumps(data)
print(s)
print(pickle.loads(s))

# ── CopyReg ──────────────────────────────────────────────────────────────────

copy_reg.dispatch_table


# ── Marshal ──────────────────────────────────────────────────────────────────

marshal.dumps(None)


# ── Importlib ────────────────────────────────────────────────────────────────

loader = importlib.machinery.ExtensionFileLoader(
    name='foo',
    pathname='/usr/lib/python3/dist-packages/foo.so'
)
spec = importlib.util.spec_from_loader(name='foo', loader=loader)
module = importlib.util.module_from_spec(spec)
assert module.foo is not None
sys.modules['foo'] = module
spec.loader.exec_module(module)


# ── Sys Internals ─────────────────────────────────────────────────