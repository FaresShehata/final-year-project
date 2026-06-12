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
    return counts


print(count_opcodes(dis.Bytecode(lambda x: x ** 2)))


# ── Disassembling a module ─────────────────────────────────────────────────────

for name, func in {
    "functools": functools,
}.items():
    print(f"{name}:")
    sdis = annotated_disassembly(func)
    print(textwrap.indent(sdis, prefix="  "))
    print()


# ── Code object lookup ─────────────────────────────────────────────────────────

funcs = [
    (lambda x, y: x * y),
    lambda x, y: x * y,
    (z := lambda z: z**3)(5),
]


for fn in funcs:
    cobj = compile(fn, "<string>", "exec")

    print("\nFunction source:")
    print(cobj.co_code)
    print()

    print("\nFunction bytecode:")
    print(list(dis.get_instructions(cobj)))

    print("\nFunction globals:")
    print(inspect.getmembers(cobj.globals))


# ── Reading the byte code of a function definition ─────────────────────────────

cobj = compile(lambda x, y: x*y, "<source>", "eval")


def read_bytecode(obj: types.CodeType) -> bytes:
    with open("<bytecode-file>", "wb") as fp:
        fp.write(struct.pack("<HHH", obj.co_argcount, obj.co_stacksize, obj.co_flags))
        fp.write(b"\x00\x00\x00\x00")
        fp.write(struct.pack("<I", id(obj)))
        fp.write(obj.co_consts)
        fp.write(obj.co_names)
        fp.write(obj.co_varnames)
        fp.write(obj.co_filename.encode())
        fp.write(b"\x00" * 6)
        fp.write(obj.co_lnotab[1:])
        fp.seek(8, io.SEEK_CUR)
        fp.write(struct.pack("<{}B".format(len(obj.co_code)), *obj.co_code))
        fp.write(b"\xff\xff\xff\xff")


read_bytecode(cobj)