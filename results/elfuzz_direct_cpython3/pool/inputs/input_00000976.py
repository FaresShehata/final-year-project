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

print_dis(lambda a, b, c: (a + b + c))
print_dis(lambda a, b, *args: (a + b + sum(args)))
print_dis(lambda a, b, **kwargs: (a + b + sum(kwargs.values())))
print_dis(lambda a, b, *, kwarg: a+b+kwarg)
print_dis(lambda a, b, /, kwarg: a + b + kwarg)
print_dis(lambda a, b, /, *, kwarg: a + b + kwarg)
print_dis(lambda a, b, /, kwarg1=None, kwarg2=None, *args, **kwargs: (
    a + b + len(args) + sum(kwargs.values()) + (kwarg1 or 0) + (kwarg2 or 0)))

# ── Code Objects ───────────────────────────────────────────────────────────────

import builtins


def print_code_object(code):
    # Print the whole thing
    print(code)
    print()

    for line_number, op in enumerate(code.co_lineoffsets):
        print(line_number, op)
    print()

    for i, (n, opname, arg, offset, pcoffset, hasconst, hasjrel, jreloffset, startsym, _nostart, noparg, noreturn, argval, argrepr) in enumerate(
            dis.get_instructions(code)):
        print(i, opname, arg, offset)
    print()

    for i, (opname, op, arg, offset, unparsed) in enumerate(
            dis.findlinestarts(code)):
        print(i, opname, arg, offset, unparsed)
    print()

<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    obj = bts.__dict__.get(f'_{bts.__name__}.{code}')

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