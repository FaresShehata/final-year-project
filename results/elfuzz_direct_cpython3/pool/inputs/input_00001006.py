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

# ── dis module ────────────────────────────────────────────────────────────────

for i in range(ord("a"), ord("z") + 1):
    print(f"ord({i}): {dis.opname[i]}")
    print(f"{i}: {dis.opname[i]}")


# ── Code Objects ──────────────────────────────────────────────────────────────


def func(a, b):
    pass


assert func.__code__.co_argcount == 2

func_code = func.__code__
assert isinstance(func_code.co_consts, tuple)

assert len(func_code.co_names) > 56

# ── ctypes ────────────────────────────────────────────────────────────────────

intp_t = ctypes.POINTER(ctypes.c_int)

s = struct.Struct("<hh")
v = s.pack(7, 11)
print(v)
print(struct.unpack_from(s.format, v))  # <- unpack_to is not a method; it's a static function
print(s.sizeof)

# ── struct ────────────────────────────────────────────────────────────────────

x = struct.Struct("<ii")
b = bytearray([97, 3, 98, 4])
d = x.unpack(b)
print(d)
c = x.pack(*d)
print(c)

a = array.array(x.typecode, (7, 9))
print(sorted(a))


class Foo(array.array):

    def __new__(cls, *args, **kwargs):  # type: ignore[no-untyped-def]
        self = super().__new__(cls, "f", *args, **kwargs)
        self._val = 1
        return self

    @property
    def val(self) -> int:
        return self._val

    @val.setter
    def val(self, value) -> None:
        self._val = value

    @property
    def length(self) -> int:
        return len(self)

    @length.setter
    def length(self, value) -> None:
        if value < 0:
            raise ValueError("Length must be positive")

        while self.length != value:
            if self.length < value:
                self.append(0.)
            else:
                del self[value - 1]

    def __getitem__(self, index: int | slice) -> float | list[float]:
        return array.array.__getitem__(self, index)

    def __setitem__(self, index: int | slice, value: float | list[float]) -> None:
        array.array.__setitem__(self, index, value)

    def append(self, item: float) -> None:
        assert not hasattr(item, "__iter__")
        array.array.append(self, item)

    def extend(self, iterable: Iterable[float]) -> None:
        for item in iterable:
            array.array.extend(self, item)

foo = Foo()
foo.val = 10
print(foo.val)
foo.append(3.14159265358979323846)
print(foo[-1])

# ── array ────────────────────────────────────────────────────────────────────

arr = array.array('h', [1, 2, 3, 4, 5])
print(arr.byteswap())

with open("test.bin", "wb") as f:
    arr.tofile(f)

