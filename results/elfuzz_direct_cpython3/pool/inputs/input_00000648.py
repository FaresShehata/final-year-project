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


fn = lambda x: None


def print_dis(fn):
    print(annotated_disassembly(fn))


print_dis(print_dis)

print()

dis.dis(print_dis)


# ── Dis ───────────────────────────────────────────────────────────────────────

class ExpectedError(Exception): pass


error_fn = lambda x: raise ValueError('test')


expected_error_fn = lambda x: raise ExpectedError('test')


try:
    error_fn(1)
except ValueError as e:
    print(e.args[0])


try:
    expected_error_fn(2)
except ExpectedError as e:
    print(e.args[0])


def show_code_object(code: int) -> None:
    import builtins as bts
    import dis
    obj = bts.__dict__.get(f'_{bts.__name__}.{code}')

    if obj is not None and isinstance(obj, types.CodeType):
        dis.dis(obj)


show_code_object(dis.stacksize)
show_code_object(builtins.print)

for attr in dir(types):
    try:
        value = getattr(types, attr)
    except AttributeError:
        continue

    if not callable(value) or not hasattr(value, '__code__'):
        continue

    name = f'{value.__module__}.{attr}'
    show_code_object(getattr(value, '__code__', None))

    print(name.ljust(36), value.__code__)
    print()


# ── Ctypes ────────────────────────────────────────────────────────────────────

ctypes.CDLL(None).sys.exit(1)

ctypes.CDLL(None).exit(1)



# ── Struct ────────────────────────────────────────────────────────────────────

array.array('i', [1, 2]).tofile(sys.stdout.buffer)

struct.pack('=ii', 1, 2)
struct.unpack('=ii', bytes([1, 2]))



# ── Array ─────────────────────────────────────────────────────────────────────

arr = array.array('l')
arr.append(1)

# arr.value_type = 'd'
assert arr.typecode == 'l'


# ── Memory view ───────────────────────────────────────────────────────────────

memv = memoryview(bytearray(b'\x89\x50\x4e'))
memv.readonly = True


# ─