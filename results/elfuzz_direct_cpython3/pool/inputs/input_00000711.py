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

print("Bytecode disassemblies")
assert annotated_disassembly(hot_path) == """
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with inspection")
assert annotated_disassembly(inspect.getsource(hot_path)) == """
  3           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               0 (2)
              4 COMPARE_OP               6 (<)
              8 POP_JUMP_IF_FALSE       19
             10 LOAD_FAST                0 (n)
             12 LOAD_FAST                0 (n)
             14 BINARY_MULTIPLY
             16 STORE_FAST               1 (total)
             18 JUMP_ABSOLUTE            5
             21 LOAD_FAST                1 (total)
             23 LOAD_GLOBAL              0 (i)
             25 BINARY_SUBTRACT
             27 STORE_FAST               1 (total)
             29 JUMP_ABSOLUTE            5
             32 LOAD_CONST               1 (None)
             34 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 3, 'BINARY_MULTIPLY': 1, 'BINARY_SUBTRACT': 2, 'JUMP_ABSOLUTE': 2, 'POP_JUMP_IF_FALSE': 1, 'RETURN_VALUE': 1}

# ───── Struct and array ───────────────────────────────────────────────────────

a = array.array('b', [1, 2, 3])     # signed char
b = array.array('B', [1, 2, 3])     # unsigned char
c = array.array('i', [1, 2, 3])     # signed integer
d = array.array('I', [1, 2, 3])     # unsigned integer
e = array.array('h', [-32768, -1, 0, 1, 32767])   # short
f = array.array('H', [-32768, -1, 0, 1, 32767])   # unsigned short
g = array.array('l', [-2147483648, -1, 0, 1, 2147483647])      # long
h = array.array('L', [-2147483648, -1, 0, 1, 2147483647])      # unsigned long
i = array.array('q', [-9223372036854775808, -1, 0, 1, 9223372036854775807])        # long long
j = array.array('Q', [-9223372036854775808, -1, 0, 1, 9223372036854775807])        # unsigned long long