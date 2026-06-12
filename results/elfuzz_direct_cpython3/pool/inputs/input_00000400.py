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
    a = n * (n - 3) // 2
    b = n ** 2
    c = (a + b) % n
    d = c + 1
    e = d * (d + 1) // 2
    return e


print(annotated_disassembly(hot_path))
print(count_opcodes(hot_path))

# ── Dis and code objects ──────────────────────────────────────────────────────

def generate_code(function_name: str | None = None, argcount: int = 0) -> types.CodeType:
    """Return an empty function object."""
    if function_name is not None:
        func = types.FunctionType(
            code=None,
            globals={},
            name=function_name,
            argdefs=tuple(),
            closure=(),
        )
    else:
        func = types.FunctionType(code=None, globals={}, argdefs=tuple())
    return func.__code__

dis.dis(generate_code('foo', 1))

# ── CTypes and struct ─────────────────────────────────────────────────────────

p = ctypes.c_int()
q = ctypes.pointer(p)

p.value = 42
assert p.value == q.contents.value

v = struct.pack('=i', 69)
assert v == b'\x01\x00\x00\x00'
u = struct.unpack('=i', v)[0]
assert u == 69

# ── Array ─────────────────────────────────────────────────────────────────────

arr = array.array('h')
arr.append(-5)
arr.extend([10, -3])
for item in arr:
    print(item)


class B(object): pass
b = B()

print(arr.buffer_info())                       # => (234872, 3)
print(b.__array_interface__['data'])           # => (234872, False)
print(array.array.frombuffer(memoryview(b), typecode='B').tolist())       # => [0]

# ── MemoryView ───────────────────────────────────────────────────────────────

m = memoryview(bytearray(range(10)))
assert m[1:3].tobytes() == b'12'

m_octets = memoryview(m).cast("B")
assert m_octets.tobytes() == b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t"

# ── Pickle ───────────────────────────────────────────────────────────────────

pickle.loads(b"\\x80\\x03c__main__\\ttest_pickle\\ta\x00.")


def test_pickle(): pass
pickle.dumps(test_pickle)

with open("test_pickle.dat", "wb") as f:
    pickle.dump((test_pickle,), f)

with open("test_pickle.dat", "rb") as f:
    test_pickle_2 = pickle.load(f)

assert test_pickle_2 is test_pickle     # same reference

# ── CopyReg and Marshal ───────────────────────────────────────────────────────

# TODO

# ── Importing modules ─────────────────────────────────────────────────────────

# ref https://docs.python.org/3/reference/import.html#import-hooks
#
# ref https://github.com/python/cpython/blob/v3.11.3/Lib/runpy.py
# ref https://