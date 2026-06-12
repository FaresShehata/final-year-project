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
    "N": "size_t",
    "f": "float",
    "F": "double",
    "d": "long double",
}

struct_name = "U"
kind = ord("N")

format_str = struct.calcsize(struct_name)

if format_str == 1:
    print(f"\n{struct_name} is a {kind_names[kind]} of size 1 byte.")
elif format_str <= 65530:
    print(f"\n{struct_name} is a {kind_names[kind]} of size up to {format_str} bytes.")
else:
    print(f"\n{struct_name} is a {kind_names[kind]} of any length.")

# ─────────── Binary representations of integers ──────────────────────────────

binary_representation_of_