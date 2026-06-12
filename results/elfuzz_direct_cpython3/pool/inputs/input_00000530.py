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
    return types.FunctionType(new_co, fn.__globals__, name=new_name, argdefs=fn.__defaults__)


class MyFunction(types.FunctionType):

    @classmethod
    def replace(cls, *, defaults=None, closure=None, globals=None, qualname=None, name=None, doc=None, argcount=None,
                kwonlyargcount=None, nlocals=None, stacksize=None, code=None, consts=None, names=None, varnames=None,
                filename=None, name_location=None, firstlineno=None, lnotab=None, freevars=None, cellvars=None):
        raise NotImplementedError("This can only be done through object mutation")

    @property
    def qualname(self):
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}"

    class __bool__(types.FunctionType):     # type: ignore[misc]
        pass                                # TODO: test this out


my_function = MyFunction(
    fn.__code__,
    fn.__globals__,
    name='big_fun',
    argdefs=fn.__defaults__,
    closure=fn.__closure__,
    func_defaults=MyFunction.defaults(),
    )

# ── Ctypes ────────────────────────────────────────────────────────────────────


class FakeCStruct(ctypes.Structure):
    _fields_: tuple[tuple[str, Any], ...]


struct_type = FakeCStruct._asdict()
assert isinstance(struct_type['some_int'], int)

x = struct.pack('<i', 69)       # little-endian int
y = struct.unpack('<i', x)[0]

z = ctypes.c_uint32.from_buffer_copy(y)
assert z.value == y

ctypes.sizeof(FakeCStruct)
ctypes.addressof(z)
ctypes.alignment(FakeCStruct)

a = array.array('f', [1.0, 2.0])

array_repr = repr(a)
print(array_repr)
print(repr(array_repr))
print(textwrap.dedent(array_repr))

b = array.array('d', [1.0, 2.0])
c = array.array('d')
for v in b:
    c.append(v)

assert id(b) != id(c), 'Array instances must be independent'
assert len(b) == len(c), "Arrays have different lengths"
assert all([v == w for v, w in zip(b, c)]), "Arrays are not equal"

m = array.array('B', bytearray([69]))
n = array.array(m.typecode)
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
        if i % 2 == 0:               # this is the hot path
            total += i * i           # it's executed many times during evaluation
    return total

print(annotated_disassembly(hot_path))

print('opcount:', len(dis.get_instructions(hot_path)))
for opcode, count in count_opcodes(hot_path).items():
    print(f'{opcode:<3} {count}')
print()

# ── Dis ───────────────────────────────────────────────────────────────────────

dis.dis(hot_path)

byte_code = hot_path.__code__.co_code
print(byte_code[::])
print()

# ── Code Objects ──────────────────────────────────────────────────────────────


def add(a, b):
    return a + b


def make_adder(n: int):
    def adder(x: int) -> int:
        return x + n
    return adder

add_5 = make_adder(5)


class GenericAdder:
    def __init__(self, n: int):
        self.n = n

    def __call__(self, x: int) -> int:
        return x + self.n


adder_5 = GenericAdder(5)

print(add.__code__)
print(make_adder.__code__)
print(GenericAdder.__code__)

print(add.__code__.co_argcount, add.__code__.co_flags & dis.WITH_CONTINUATION)
print(make_adder.__code__.co_argcount, make_adder.__code__.co_flags & dis.WITH_CONTINUATION)
print(GenericAdder.__code__.co_argcount, GenericAdder.__code__.co_flags & dis.WITH_CONTINUATION)

print(add.__code__.co_varnames[:add.__code__.co_argcount])             # positional arguments
print(add.__code__.co_freevars[:add.__code__.co_cellvars])              # free variables
print(add.__code__.co_consts)                                         # constants
print(add.__code__.co_names)                                          # names used as identifiers
print(add.__code__.co_filename, add.__code__.co_firstlineno)          # source filename and line number of first instruction
print(add.__code__.co_lnotab)                                         # mapping from byte offsets to line numbers
print(add.__code__.co_stacksize)                                      # estimated size of stack needed by function (in words)
print(add.__code__.co_flags, dis.hasfree(add.__code__))                # flags and free variables
print(add.__code