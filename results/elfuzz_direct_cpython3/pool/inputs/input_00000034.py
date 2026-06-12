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
        if instr.opname.startswith("LOAD"):
            opcode = instr.opname[5:]
        else:
            opcode = instr.opname.lower()

        counts[opcode] = counts.get(opcode, 0) + 1
    return counts


def annotate_opcode_counts(fn) -> str:
    counts = count_opcodes(fn)

    def op(name: str, offset: int) -> str:
        return f"{name:<8}: {counts[name]:>4} @ {offset}"

    buf = io.StringIO()
    for offset, instr in enumerate(dis.get_instructions(fn)):
        print(op(instr.opname, offset), end=" ", file=buf)
    return buf.getvalue()


def get_function_code(fn) -> types.CodeType:
    """Get the compiled code object for a function or method."""
    return fn.__code__

# ── Disassembler API ──────────────────────────────────────────────────────────


def disasm(obj, *, show_source=False) -> str:
    """Disassemble an object's code, with source and bytecodes included."""
    if hasattr(obj, "__code__"):       # Callable?
        code = obj.__code__
    elif isinstance(obj, (types.CodeType, types.FunctionType)):  # CodeObject?
        code = obj
    else:
        raise TypeError(f"cannot disassemble {type(obj).__name__}")

    buf = io.StringIO()
    dis.disassemble(code, file=buf)
    if show_source:
        buf.write("\n\n")
        src_lines = inspect.getsource(obj).splitlines()
        max_src_line_len = max(map(len, src_lines))
        for line_no, line in enumerate(src_lines[code.co_firstlineno - 1:], start=1):
            if line_no == code.co_firstlineno:
                before = after = ""
            elif line_no < code.co_firstlineno:
                before = " " * max_src_line_len
            elif line_no > code.co_firstlineno:
                after = " " * max_src_line_len
            buf.write(f"{line_no:>3} | '{before}{line}{after}'|{max_src_line_len - len(line):<3}\n")
        buf.seek(-len(after), io.SEEK_END)
        buf.truncate()
    return buf.getvalue()


# ── Tracing / wrapping with copyreg ───────────────────────────────────────────


def add_to_traceable_types(cls: type[Any]) -> None:
    import copyreg
    copyreg.pickle    return new_fn


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
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

