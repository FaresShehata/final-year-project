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
    dis.get_instructions(hot_path), key=lambda t: t[0] == "LOAD_CONST"
):
    print(f"{opname:<15} {num_operands}")

print("\n\n")

for opname, num_operands in sorted(
    dis.get_instructions(hot_path),
    key=lambda t: t[0] in {
        "SET_LINENO",
        "JUMP_FORWARD",   # no-op; just a place holder for jump target addresses
        "POP_JUMP_IF_FALSE",
        "POP_JUMP_IF_TRUE",
        "CONTINUE_LOOP",
        "JUMP_ABSOLUTE",
        "JUMP_BACKWARD",
        "CALL_FUNCTION",
        "RETURN_VALUE",
    },
):
    print(f"{opname:<15} {num_operands}")

print("\n\n")
counts = count_opcodes(hot_path)
for name, count in sorted(counts.items()):
    if count >= 3 and name.startswith("LOAD_"):
        print(name)

print("\n\n")
del counts
gc.collect()                  # to force collection of hot_path's cache

# ── Dis ──────────────────────────────────────────────────────────────────────

# Disassemble the function object itself.
dis.dis(hot_path)


def load_const_fn(fp, klass=None):
    """Load a constant from a .pyc or .pyo file."""
    global co_consts
    tp = fp.read(4)
    assert len(tp) == 4 and ord(tp[0]) == 0xc4
    tp += fp.read(5)            # length
    tp += fp.read(ord(tp[-1]))
    if klass is not None:
        obj = klass.__new__(klass, tp)
        obj.fp = fp
        obj.next = None
        obj.lineno = 0
        obj.co_consts = co_consts = []
    else:
        obj = eval(tp.decode(), {"__builtins__": None}, {})
    return obj


class PycLoader(importlib.machinery.BuiltinImporter):

    def find_module(self, fullname, path=None):
        if fullname != "__main__":
            return super().find_module(fullname)
        from py_compile import PyCompileError
        try:
            with open('seed-04-lowlevel.py') as f:
                pyc_data = f.read()
        except FileNotFoundError:
            raise PyCompileError("no such file or directory: 'seed-04-lowlevel.py'")
        else:
            return self._load_pyc(pyc_data)


pypath