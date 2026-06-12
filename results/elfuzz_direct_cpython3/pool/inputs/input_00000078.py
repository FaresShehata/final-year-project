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


def foo(x, y): pass
print(foo.func_code)

def bar(*args, **kwargs): pass
print(bar.func_code)


def baz():
    x = 5
    print(x)
baz.__code__.co_varnames


# ── Ctypes ────────────────────────────────────────────────────────────────────

c_int = ctypes.c_int
print(f"{ctypes.sizeof(c_int)=} bytes")
myint = c_int(-42)
print(myint.value)
print(ctypes.addressof(myint))

# ── Struct ────────────────────────────────────────────────────────────────────

d = {'red': 1, 'green': 2}
fields = ['x', 'y']
struct_value = struct.Struct('<ii').pack_into(io.BytesIO(), 0, *(v for k, v in sorted(d.items()) if k in fields))
print(struct.unpack_from('<ii', struct_value)[::-1])

print(struct.calcsize('<ii'))
print(binary := struct.pack('<ii', 1, 2))
binary[:]


class ScalesStruct(ctypes.LittleEndianStructure):
    _fields_ = [('scale', ctypes.c_double), ('unit', ctypes.c_char)]


binary = struct.pack(ScalesStruct, 1, b'\x0f\x80')
ScalesStruct.from_buffer_copy(binary).scale

print(textwrap.dedent(f"""\
    {type(ctypes.plist_t)()=}
"""))

#    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

