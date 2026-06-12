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
    for _ in range(2 ** n):
        total += 1 + (total * total - 3) // 5 + (-8 if total else 0) + 7
    return total


def main() -> None:
    print("\nBytecode introspection\n")
    print(f"{annotated_disassembly(hot_path)}")
    print(count_opcodes(hot_path))


if __name__ == "__main__":
    main()

# ───────────────────────────────────────────────────────────────────────────────

# ── Dis ────────────────────────────────────────────────────────────────────────

print("\nDis assembly of a function\n")


class MyInt(int):

    def __init__(self, value: int | str) -> None:
        super().__init__()
        self.value = int(value)


def func(myint: MyInt) -> str:

    my_int = MyInt("test")

    s: str = "Hello World!"[:myint]

    return f"Result is {s}"


print(dis.dis(func))


# ───────────────────────────────────────────────────────────────────────────────

# ── Code object ────────────────────────────────────────────────────────────────

print("\nCode object used by a function\n")


class MyInt(int):

    def __init__(self, value: int | str) -> None:
        super().__init__()
        self.value = int(value)


def func(myint: MyInt) -> str:

    my_int = MyInt("test")

    s: str = "Hello World!"

    return f"Result is {s[0:myint]}"

f_code = func.__code__

print("Function name:", f_code.co_name)
print("Source file name:", f_code.co_filename)

if isinstance(f_code.co_consts, list):
    const_iter = iter(f_code.co_consts)
else:
    const_iter = iter(list(f_code.co_consts))

for i, item in enumerate(const_iter, start=1):
    print(f"Constant {i}: {item}")

# ───────────────────────────────────────────────────────────────────────────────

# ── Ctypes ────────────────────────────────────────────────────────────────────

print("\nCtypes example with class\n")


class MyClass(ctypes.c_uint64):

    _id = 1

    def __new__(cls, value: int | str) ->