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
            total -= i * i
    return total


print(annotated_disassembly(hot_path))
print(count_opcodes(hot_path))

# ───────────────────────────────────────────────────────────────────────────────

# ── Dis ────────────────────────────────────────────────────────────────────────

target_pyc = "seed_04.pyc"

with open(target_pyc, 'wb') as f:
    f.write(b'\x03\x00\x00\x00\x05\x00\x00\x00\xf7\x00\x00\x00')
    f.write(struct.pack('h', -18))

dis.disassemble(target_pyc)

# ───────────────────────────────────────────────────────────────────────────────

# ── Code object representation ────────────────────────────────────────────────

CODE_OBJ_SIZE = 96   # for CPython 3.9.7

raw_code_obj = b"\x03" \
               b"\x00" \
               b"\x00" \
               b"\x00" \
               b"\xff\xff\xff\xff" \
               b"\xff\xff\xff\xff" \
               b"\xff\xff\xff\xff" \
               b"\xff\xff\xff\xff" \
               b"\xfe" \
               b"\xff" \
               b"\xf0" \
               b"\xff" \
               b"\xff" \
               b"\xf1" \
               b"\xff" \
               b"\xf2" \
               b"\xff" \
               b"\xf3" \
               b"\xff" \
               b"\xf4" \
               b"\xff" \
               b"\xf5" \
               b"\xff" \
               b"\xf6" \
               b"\xff" \
               b"\xf7" \
               b"\xff" \
               b"\xf8" \
               b"\xff" \
               b"\xf9" \
               b"\xff" \
               b"\xfa" \
               b"\xff" \
               b"\xfb" \
               b"\xff" \
               b"\xfc" \
               b"\xff" \
               b"\xfd" \
               b"\xff" \
               b"\xfe" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff" \
               b"\xff"               b"\xfe" \
               b"\xf2" \
               b"\xfe" \
               b"\xf1" \
               b"\xfe" \
               b"\xf0" \
               b"\xfe" \
               b"\xef" \
               b"\xfe" \
               b"\xee" \
               b"\xfe"