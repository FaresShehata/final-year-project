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

print(dis.dis(hot_path))
print(f"{len(dis.get_instructions(hot_path)):} instructions")

disassemble_obj = dis.Bytecode(hot_path).disassemble()
for line in disassemble_obj.split("\n"):
    print(line)

# ── Ctypes ────────────────────────────────────────────────────────────────────

ctypes.c_int(-1)
ctypes.c_float(float("nan"))
ctypes.c_double(float("inf"))

# ── Struct ────────────────────────────────────────────────────────────────────

# struct.pack('i', ...): pack ints to bytes or vice versa
# struct.unpack('i', ...): unpack the bytes into an int
# struct.calcsize(): calculate size of packed data based on format string

# https://docs.python.org/3/library/struct.html

# ── Array ─────────────────────────────────────────────────────────────────────

array.array('i', [x**2 for x in range(5)])

# ── Memoryview ────────────────────────────────────────────────────────────────

memoryview(bytearray([10, 20, 30]))

# ── Pickle ────────────────────────────────────────────────────────────────────

pickle.dumps(hot_path)
pickle.loads(pickle.dumps(hot_path))

# ── Copyreg ───────────────────────────────────────────────────────────────────

class MyClass:
    def __init__(self, value: int | float) -> None:
        self.value = value
    
    @classmethod
    def from_bytes(cls, data: bytes) -> MyClass:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        
        try:
            value = pickle.loads(data)
        except Exception as exc:
            raise ValueError(exc.args[0]) from exc
        
        return cls(value)


MyClass.from_bytes(b"\x8b\x03\x00\x00\x00\x00\x00\x00")


def my_copy_reg(obj: object) -> None:
    """Register a custom copy function.

    This registers `my_pickle` with the built-in `copy` module.
    """
    pickle.register(MyClass)(my_pickle)


def my_pickle(obj: MyClass) -> bytes:   # Custom pickling function
    return pickle.dumps(obj.value)


with open(__file__, "rb") as fp:
    content = fp.read()

content_packed = pickle