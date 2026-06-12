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
             23 LOAD_FAST                0 (n)
             25 BUILD_SLICE              1
             27 BINARY_SUBTRACT
             29 STORE_FAST               1 (total)
             31 JUMP_ABSOLUTE            5
             34 LOAD_CONST               1 (None)
             36 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'COMPARE_OP': 1, 'POP_JUMP_IF_FALSE': 1, 'BINARY_MULTIPLY': 1, 'STORE_FAST': 2, 'JUMP_ABSOLUTE': 2, 'BUILD_SLICE': 1, 'BINARY_SUBTRACT': 2, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with dis.symtable")
assert annotated_disassembly(dis.symtable(hot_path)) == """
Disassembling hot_path:
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""


# ─────── Code Objects ─────────────────────────────────────────────────────────

def test_code_object() -> None:

    def foo(x: int, y: int, z: float) -> str:
        pass

    co = foo.__code__

    assert co.co_argcount == 3
    assert co.co_varnames == ("x", "y", "z")

    # TODO: add more tests


# ───