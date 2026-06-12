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


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    fmt = f">f f f {len(points)}H"
    size = struct.calcsize(fmt)
    raw = bytearray(size)
    endianness = ">" if sys.byteorder == "little" else "<"
    point_fmt = endianness + f"f f f H"
    offset = HEADER_SIZE
    for idx, (x, y, z, n) in enumerate(points):
        start = offset + idx * struct.calcsize(point_fmt)
        end = start + struct.calcsize(point_fmt)
        struct.pack_into(point_fmt.format(*points[idx]), raw, start, x, y, z, n)
    return raw


def main():
    print("seed 04")

    def nn(n: int | float) -> tuple[int, int]:
        return divmod(int(n), 2)

    print(f"{nn.__code__.co_nlocals} locals")
    print(nn.__code__)
    print(divmod.__code__)

    @types.coroutine
    async def gen(pow: int):
        for val in range(pow):
            yield pow ** val

    co = gen.__code__
    print(f"{co.co_argcount} args, {co.co_kwonlyargcount} kw-only args")
    print(co.co_varnames)

    def foo(a: int, b: str) -> str:
        pass

    print(foo.__code__)
    print(count_opcodes(foo))
    print(hot_path(1_000_000))

    def bar(a: int, *, kw: str) -> str:
        pass

    print(bar.__code__)
    print(count_opcodes(bar))
    print(hot_path(1_000_000))

    print(clone_with_name(gen, "__gen"))

    print(make_adder_from_bytecode(5).__code__)

    print("\nCode object surgery:")
    print(count_opcodes(make_adder_from_bytecode(5)))

    print("\nBytecode introspection:")
    print(textwrap.indent(annotated_disassembly(sys.executable), " "))
    print(textwrap.indent(str(count_opcodes(hot_path)), " "))

    print("\nFrame inspection:")
    print("\n".join(depth_probe()))
    frame = sys._getframe()  # noqa: PLR2004
    print(caller_info())
    print(caller_info(depth=-1))

    print("\nstruct:")
    points = [(0., 0., 