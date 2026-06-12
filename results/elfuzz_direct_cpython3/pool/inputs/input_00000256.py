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


def get_instructions(fn) -> dict:
    base_instr = "<unknown>"
    counts = count_opcodes(fn)

    def _get_instr(instr):
        if base_instr == "<unknown>" and instr.base is not None:
            base_instr = instr.base.opname
        return instr.offset, f'{instr.opname}({",".join(map(str, instr.argvals))})'

    return sorted([(v, _get_instr(instr)) for k, v in counts.items()])


def get_source(fn) -> str:
    with open(inspect.getsourcefile(fn)) as fp:
        return fp.read()


def get_docstring(fn) -> str | None:
    return fn.__doc__ or ""


def compile_fn(fn, filename="<fn>", flags=None) -> types.CodeType:
    assert isinstance(fn, types.FunctionType)
    return compile(get_source(fn), filename, "exec", flags or "exec")


def build_frame(f_globals: dict[str, Any], f_locals: dict[str, Any]) -> types.FrameType:
    return types.FrameType(
        globals=f_globals,
        locals=f_locals,
        f_back=sys._getframe(),
        f_trace=None,
        f_code=get_code_obj(type(f_globals)),
    )


def get_source_lines(obj: object) -> tuple[list[str], int]:
    nlines = obj.co_firstlineno - 1
    lines = inspect.getsourcelines(obj)[0][nlines:]
    return lines, nlines


def get_bytecode(obj: object) -> bytes:
    return marshal.dumps(obj.co_code)


# ── ctors & destructors ───────────────────────────────────────────────────────

def make_nonzero(x: object, y: object) -> bool:
    if x != y:
        return True
    else:
        raise ValueError("zero")


def make_zero(x: object, y: object) -> object:
    return 0


# ── Python internals ──────────────────────────────────────────────────────────

def get_sys_modules() -> list[object]:
    return [sys.modules[m.name] for m in sys.builtin_module_names]


def get_sys_path() -> list[str]:
    return [p.decode(sys.getfilesystemencoding()) for p in sys.path]


def get_builtin_functions() -> list[types.BuiltinFunctionType]:
    return [getattr(types, f) for f in dir(types)]


def get_meta_classes() -> list[type]:
    return [m for m in sys.meta_class    return {
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

