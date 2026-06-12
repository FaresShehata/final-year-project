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
        fp.write(obj.co_freevars)
        fp.writelines(
            (
                b"\x00" + struct.pack("<B", len(p)) + p
                for p in obj.co_cellvars
            )
        )

        # Write constants
        for const in obj.co_consts:
            if isinstance(const, tuple):
                continue
            elif isinstance(const, str):
                fp.write(const.encode())
            else:
                fp.write(const.to_bytes(4, byteorder="little"))

        # Write symbols
        for sym in obj.co_names:
            fp.write(sym.encode())

        # Write free variables
        for var in obj.co_freevars:
            fp.write(var.encode())


def write_bytecode(obj: types.CodeType, path: str) -> None:
    with open(path, "rb+") as fp:
        data = read_bytecode(obj)
        if fp.read(1) != b"I":
            raise ValueError("Invalid bytecode format.")
        fp.write(data)


write_bytecode(cobj, "<bytecode-file>")

with open("<bytecode-file>", "rb") as fp:
    bdata = fp.read()

with open("<func-def>", "wt") as fp:
    fp.write("\t".join(str(x) for x in cobj.co_code))

with open("<func-def>", "rt") as fp:
    cdata = fp.readlines()[1:]

assert bdata == "".join(cdata), f"{bdata}\n{cdata}"


# ── Read/write closures from/to bytecode files ──────────────────────────────────

closures = []


def get_closures(code: types.CodeType) -> list[tuple[type, Any]]:
    """Get closure values from a code object.

    :param code: A code object.
    :return: The closure values.
    """
    global closures
    closures.clear()
    try:
        if code.co_flags & 0b0000'0001:
            raise ValueError("This is not a closure.")

        for cell in code.co_cellvars:
            closures.append((types.CellType, code.cell_contents[cell]))

        for var in code.co_freevars:
            closures.append((cell_type, code.__closure__[var]))
    except AttributeError:
        pass
    finally:
        return closures


def set_closures(code: types.CodeType, objs: list[tuple[Any, type]]) -> None:
    """Set closure values into a code object.

    :param code: A code                return True
        return False
    return _or(ps)


def and_(*ps: bool) -> bool:
    """Church conjunction."""
    def _and(ps):
        for p in ps:
            if not p():
                return False
        return True
    return _and(ps)


def implies(a: bool, b: bool) -> bool:
    """Church implication."""
    return not_(a)() or b()


def iff(a: bool, b: bool) -> bool:
    """Church equivalence."""
    return a() == b()


def zero() -> int:
    """Zero function."""
    return 0


def succ(n: int | str) -> int:
    """Successor function."""
    n += 1
    return n


def pred(n: int) -> int:
    """Predessor function."""
    n -= 1
    return n


def add(m: int, n: int) -> int:
    """Church addition."""
    m = int(m)
    n = int(n)

    def _add(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = succ(result)
            m = pred(m)
        while n > 0:
            result = succ(result)
            n = pred(n)
        return result
    return _add


def mul(n: int, m: int) -> int:
    """Church multiplication."""
    m = int(m)
    n = int(n)

    def _mul(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = add(result, n)
            m = pred(m)
        return result
    return _mul


def inc(n: int) -> int:
    """Church increment."""
    return add(1, n)


def dec(n: int) -> int:
    """Church decrement."""
    return sub