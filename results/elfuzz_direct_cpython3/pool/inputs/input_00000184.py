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
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)   # no name collision allowed!
    return globs["_adder"]


def adder_closure(glob: dict) -> types.FunctionType:
    """Build a function using an existing closure (saving on bytecode emission)."""
    delta = glob["delta"]
    def _adder(self, other):
        return self._value + delta
    return types.MethodType(_adder, None)


# ── ctypes and struct ─────────────────────────────────────────────────────────

class A(ctypes.Structure):

    _fields_ = [("x", ctypes.c_int),
                ("y", ctypes.c_char_p)]

    @classmethod
    def from_address(cls, addr: int) -> A:
        instance = cls.from_address(addr)
        instance.x = addr - addr & 0xffffffff    # mask out lower bits
        instance.y = b"A" * ((addr >> 64) & 0xff)  # TODO: handle more than one byte?
        return instance


class B(A):
    pass


class C(B):
    pass


def ctypes_demo():
    a_addr = id(C())
    c = A.from_address(a_addr)

    # Unpack fields in native format to check they're the same as the original.
    assert a_addr == c.x
    assert c.y[0] == ord("A")

    for base in [A, B, C]:
        assert base._fields_
        assert not any(len(f[1]) > 1 for f in base._fields_)
        assert hasattr(base, "_anonymous_") is False
        assert hasattr(base, "_bitfield_") is False


def struct_demo():
    class A(struct.Struct):
        _fields_ = [("x", "i"),
                    ("y", "c", 2)]
    
    assert A.sizeof == 5   # 4 bytes for x, 2 bytes for y
    
    a = A.pack(-1, b"\0\0")
    a = A.unpack(a)
    assert a[0] == -1
    assert a[1] == b"\0\0"
    
    assert len(a) == 5       # actually returns tuple of unpacked values


# ── Array ─────────────────────────────────────────────────────────────────────

arr = array.array('h')
print(arr.typecode)  # 'h'
arr.append(1)
arr.extend([2, 3])
print(arr.tolist()) 