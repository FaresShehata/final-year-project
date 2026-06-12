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
        elif i < n // 3:
            total -= i * i - 2 * i
        else:
            total *= 9 / (i + 1)
    return total


# ── Dis ───────────────────────────────────────────────────────────────────────

disassembled_code = annotated_disassembly(hot_path)

for line in textwrap.wrap(disassembled_code, initial_indent=" ", max_lines=64):
    print(line)


# ── Code Objects ──────────────────────────────────────────────────────────────

foo_code_object = hot_path.__code__

code_name = foo_code_object.co_name
code_filename = foo_code_object.co_filename
code_flags = hex(foo_code_object.co_flags)
code_bytecode = foo_code_object.co_code
code_line_num = foo_code_object.co_lnotab
source = foo_code_object.co_firstlineno

if source > 0:
    with open(code_filename, encoding='utf-8') as fp:
        lines = fp.readlines()[source:]
else:
    lines = []

print(f"{code_name}\n{lines}")


# ── Ctypes ───────────────────────────────────────────────────────────────────-

x = ctypes.c_int.from_buffer(bytearray(b'\x00\x00'))
assert x.value == 0
y = ctypes.c_uint.from_buffer(bytearray(b'\xff\xff'), 0)
assert y.value == 0xffff
z = ctypes.c_double.from_buffer(bytearray(b'\xfe' * 8), 0)
assert z.value == -1e37


# ── Struct ───────────────────────────────────────────────────────────────────

A = struct.Struct("hh")      # "size" is an empty field

assert A.size == 4           # 4 bytes for each value
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    
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