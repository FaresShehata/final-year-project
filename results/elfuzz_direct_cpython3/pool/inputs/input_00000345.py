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

def annotated_disassembly(fn):
    def wrapper(*args, **kwargs):
        print("Function signature:")
        print(inspect.signature(fn))
        print("")
        print("Bytecode:")
        print(dis.code_info(fn))
        print("")
        print("Disassembled")
        fn(*args, **kwargs)

    return wrapper


@annotated_disassembly
def hot_path():
    global _a, _b
    _a = 5 * 7
    _b = 9 + _a + 8
    _c = _b // _a
    _d = _b - _c
    _e = 6 * (_c + 2)**2
    _f = _d + 2**_a
    _g = _e - _f
    return _g


def count_opcodes(path) -> int:
    opmap = dis.opmap
    total = 0
    for instr in path.co_code.split(OPCODE_DELIM):
        opcode = ord(instr[0])
        if opcode >= 0 and opcode <= 255:
            n = (opmap.get(opcode, 0) << 8) | opmap.get(ord(instr[-1]), 0)
            total += n
        else:
    <|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>        total += n
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

