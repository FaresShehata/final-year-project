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
    while True:
        total += n
        if total > 1_000_000:
            break
    return total


def is_true(val) -> bool:
    return not (val is False or val == 0 or val is None)


def public_names(obj) -> tuple[str, ...]:   # from collections.abc.Mapping
    return tuple(name for name in dir(obj) if not name.startswith("_"))


def private_names(obj) -> tuple[str, ...]:  # from collections.abc.Mapping
    return tuple(getattr(obj, "__{name}__".format(name=name), ()) for name in dir(obj))


def show_code(f) -> str:
    buf = io.StringIO()
    print(type(f))
    dis.show_code(f, buf)
    return buf.getvalue()


def show_frame(frame=None) -> str:
    if frame is None:
        frame = sys._getframe().f_back
    buf = io.StringIO()
    dis.show_frame(frame, buf)
    return buf.getvalue()


def show_lineage(cls) -> str:
    buf = io.StringIO()
    dis.show_lineage(cls, buf)
    return buf.getvalue()


def show_pretty(self):                     # from collections.abc.Sequence
    lines = []
    for item in self:
        lines.append(repr(item))
    return "\n".join(lines)


def show_stack(stack_size=3) -> str:
    buf = io.StringIO()
    dis.show_stack(buf, stack_size)
    return buf.getvalue()


def show_unbound_methods(methods) -> str:
    buf = io.StringIO()
    dis.show_unbound_methods(methods, buf)
    return buf.getvalue()



# ── dis ──────────────────────────────────────────────────────────────────────

print("\n--- dis ---\n")

print(annotated_disassembly(show_code(sys.__open__)))
print(dis.cachefunc(func=show_code, argnames=["fn"]))
print(count_opcodes(hot_path))

print("\n--- show_code ---\n")

print(show_code(sys.__open__))
print(show_code(lambda: 1 / 0))

print("\n--- show_frame ---\n")

print(show_frame())
print(show_frame(inspect.currentframe()))

print("\n--- show_lineage ---\n")

print(show_lineage(dict))

print("\n--- show_pretty ---\n")

print(show_pretty([1, 2, 3]))

print("\n--- show_stack ---\    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

