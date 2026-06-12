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
    print(f">>> {fn.__name__}()")
    try:
        with io.StringIO() as buf:
            dis.dis(fn, file=buf)
            return buf.getvalue()
    finally:
        del fn


print("\n\n┌───────────────────────────────────────────────────┐")
print("│                  Bytecode introspection             │")
print("└───────────────────────────────────────────────────┘\n")

from low_level_python.bytecode_introspect import annotated_disassembly

print(">>> annotated_disassembly(annotated_disassembly)\n")
disassembled_code = annotated_disassembly(annotated_disassembly)

for line in disassembled_code.splitlines():
    print(line)

print("\n\n┌───────────────────────────────────────────────────┐")
print("│                Function introspection               │")
print("└───────────────────────────────────────────────────┘\n")

print(">>> annotated_disassembly(inspect.getsource(annotated_disassembly))\n")
disassembled_source = annotated_disassembly(inspect.getsource(annotated_disassembly))

for line in disassembled_source.splitlines():
    print(line)

print("\n\n┌───────────────────────────────────────────────────┐")
print("│                    Code Objects                     │")
print("└───────────────────────────────────────────────────┘\n")

from types import CodeType
from types import CodeType

codeobj = type(
    "CodeObject",
    (),
    {
        "__init__": lambda self: None,
        "__str__": lambda self: str(self.co_name),
    },
)

call_args = (
    "arg1",
    "arg2",
    "arg3",
    "arg4",
    "arg5",
    "arg6",
    "arg7",
    "arg8",
    "arg9",
    "arg10",
    "arg11",
    "arg12",
)

argspec = inspect.ArgSpec(args=("a", "b"), var="c", kw=None, defaults=(None,) * 2)

func_code = codeobj(*call_args).co_code
func_co_names = codeobj(*call_args).co_names
func_co_varnames = codeobj(*call_args).co_varnames
func_co_argcount = codeobj(*call_args).co_argcount
func_co_kwonlyargcount = codeobj(*call_args).co_kwonlyargcount
func_co_stacksize = codeobj(*call_args).co_stacksize
# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

