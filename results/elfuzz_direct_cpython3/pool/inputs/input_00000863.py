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
    raise Exception("Unexpected number of parameters.")

print(CO.co_kwonlyargcount)
print(CO.co_flags)

# ── ctors for CodeObjects ───────────────────────────────────────────────────-

# There are two ways to create a code object:

class CoFactory(importlib.abc.CodeRegistryType):
    @classmethod
    def create_code(cls, *args) -> types.CodeType:
        # ...
        pass


co_factory = CoFactory()
new_co = co_factory.create_code(...)


# ── Struct and Array ──────────────────────────────────────────────────────────

NUMPY_TYPE = "i8"
ARRAY = array.array(NUMPY_TYPE)
ARRAY.append(-123)
ARRAY.append(456)

with ARRAY.buffer as buffer:
    print(buffer.format)
    print(bytes.frombuffer(buffer))

STRUCT = struct.Struct(NUMPY_TYPE)
bytes_ = STRUCT.pack(-123, 456)
print(bytes_)
array_ = array.array(NUMPY_TYPE)
array_.frombytes(bytes_)
print(array_)

# ── MemoryView ───────────────────────────────────────────────────────────────

MEMORYVIEW = memoryview(bytearray(b'\x01\x02'))
print(MEMORYVIEW.tolist())


# ── Pickle ───────────────────────────────────────────────────────────────────

PICKLE_BYTES = b"\x80@\x00\x00\x00\x89\x04\x00\x00\x00\x00\x00\x00q\x01\x00\x00\x00foo"

class MyPickler(pickle.Pickler):
    def persistent_id(self, obj):
        if isinstance(obj, int):
            return f'ID({obj})'
        else:
            return None

my_pickler = MyPickler(io.BytesIO())
my_pickler.persistent_id(42)
my_pickler.dump(PICKLE_BYTES)
MY_PICKLE_BYTES = my_pickler.dumps()
assert MY_PICKLE_BYTES == PICKLE_BYTES


# ── CopyReg & Marshal ────────────────────────────────────────────────────────

DUMP_REGISTRY = {}
LOAD_REGISTRY = {}

@pickle.register_pickle(pre_dump=lambda _, s, _ : DUMP_REGISTRY[s])
def dump_int(s, i: int):
    print('dumping integer')
    return marshal.dump(i, s)

@pickle.register_pickle(post_load=lambda _, s, _ : LOAD_REGISTRY[s])
def load_int(s):
    print('loading integer')
    return marshal.load(s)

print(DUMP_REGISTRY)
print(LOAD_REGISTRY)

int_bytes = pickle.dumps(42)
print(int_bytes)

unpickled_int = pickle.loads(int_bytes)
print(unpickled_int)

print(DUMP_REGISTRY)
print(LOAD_REGISTRY)

# ── ImportLib & SysInternals ─────────────────────────────────────────────────

MODULE_NAME = 'example'

sys.path.append('/path/to/python/modules')

spec = importlib.util.spec_from_file_location(MODULE_NAME, '/path/to/example.py')
module = importlib.util.module_from_spec(spec)

spec.loader.exec_module(module)

print(module.__doc__)


# ── Frame Inspection ─────────────────────────────────────────────────────────

def annotate(frame):
    print(f"Filename: {frame.f_code.co_filename}")
    print(f"Name: {frame.f_code.co_name}")
    print(f"Line Number: {frame.f_lineno}")

FRAME = inspect.currentframe()
annotate(FRAME)


# ── GC & Tracemalloc ──────────────────────────────────────────────────────────

gc.collect()

tracemalloc.start()

try:
    ...
finally:
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("traceback")
    for stat in top_stats[:1]:
        print(stat.traceback.format()[0])


# ── Weakref & Slots ───────────────────────────────────────────────────────────

class AClass:
    __slots__ = ['b']

    def __init__(self, b):
        self.b = b

a = AClass(123)
weakref.ref(a)

class BClass:
    def __init__(self, b):
        self.b = b

    def __getattribute__(self, attr):
        if attr != 'b':
            return super().__getattribute__(attr)
        b = super().__getattribute__('b')
        return b + 1

b = BClass(123)