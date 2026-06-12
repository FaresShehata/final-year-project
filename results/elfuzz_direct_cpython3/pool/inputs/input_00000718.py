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
    x = n - 1                        # (x-1)-1 => x-2
    y = n + 1                        # (n+1)+1 => n+2
    z = x * y                        # (x*y)*y => x*y**2
    return z                         # return z => return x*y**2


print(annotated_disassembly(hot_path))

print("\n\n")
for opname, num_operands in sorted(
    dis.get_instructions(hot_path), key=lambda t: t[0]
):
    print(f"{opname:<8}{num_operands:>3}")

print("\n\n")
counts = count_opcodes(hot_path)
for name, count in counts.items():
    if count > 1:
        print(name, f"({count} times)")

# ───── Struct and array ──────────────────────────────────────────────────────

array_name = "U"
kind = ord("N")  # c, b, B, h, H, i, I, l, L, q, Q, n, N, f, F, d, D, s, S, p, P

kind_names = {
    "c": "char",
    "b": "signed char",
    "B": "unsigned char",
    "h": "short",
    "H": "unsigned short",
    "i": "int",
    "I": "unsigned int",
    "l": "long",
    "L": "unsigned long",
    "q": "long long",
    "Q": "unsigned long long",
    "n": "ssize_t",
    "N": "uintptr_t",
    "f": "float",
    "F": "double",
    "d": "long double",
    "s": "string",
    "S": "unicode",
    "p": "void*",
}

struct_format = "<{}{}".format(kind_names[array_name], kind)

assert len(struct_format) == 5
assert struct_format.encode() == struct.pack(struct_format, 1)

a = array.array(array_name, [1])
assert a.buffer_info()[1] is a.data
assert a.tostring() == struct.pack(struct_format, 1)

b = array.array(array_name, [2])
c = a + b
assert c.tolist() == [1, 2]

data = struct.unpack(struct_format, c.tobytes())
assert data[0] == 1
del c

try:
    d = array.array(array_name, [0, 1])
except struct.error as exc:
    assert isinstance(exc.__cause__, OverflowError)

e = array.array(array_name, [[1], [2]])
assert e.tolist() == [[1], [2]]


class MyArray(array.ndarray):     # subclassing works just like regular array
    pass


A = MyArray([1, 2])

with A.view(ctypes.c_int64) as view:
    view[:] = 3

assert A.tolist() == [3, 3]


# ─────────— Copyreg ──────────────────────────────────────────────────────────

class X(object):

    def __getstate__(self):
        return {"attr": self.attr}


class Y(X):
    attr = 10


pickle.dumps(Y())


def my_copyreg_reconstructor(obj):
    return obj.zoo


copyreg.pickle(tuple, my_copyreg_reconstructor)


# ───── Marshal ───────────────────────────────────────────────────────────────

assert marshal.loads(marshal.dumps(None)) is None
assert marshal.loads(marshal.dumps(b'abc')) == b'abc'


# ────────── Pickle tools ─────────────────