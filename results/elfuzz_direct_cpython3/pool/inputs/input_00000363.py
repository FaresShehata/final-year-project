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
    current_label = ""
    for i, op in enumerate(dis.findlinestarts(fn)):
        label = dis.opname[op]
        if label.startswith('EXTENDED_ARG'):
            continue
        elif label == 'SETUP_LOOP' and not current_label:
            current_label = f"{i}.{label}"
        elif label.endswith('_LOOP') and current_label:
            counts[current_label] = counts.get(current_label, 0) + (i - HEADER_SIZE // 8)
            current_label = ""
    return counts


def get_instructions(fn) -> list[tuple[int, str]]:
    instructions: list[tuple[int, str]] = []
    for i, op in enumerate(dis.findlinestarts(fn)):
        label = dis.opname[op]
        if label.startswith('EXTENDED_ARG'):
            continue
        elif label == 'SETUP_LOOP':
            instructions.append((i, label))
        elif label.endswith('_LOOP'):
            instructions.extend([(i, label)])
    return instructions


def get_instruction_sources(fn) -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {}
    for lineno, instruction in get_instructions(fn):
        source = fn.co_lnotab[lineno * 2 : lineno * 2 + 2]
        if source:
            offset = ord(source[-1])
            source = fn.co_code[lineno * 2 :]
            instruction += f"(offset {hex(offset)}) "
        instruction += f"(source line {dis.showlinerange(fn)}})"
        if instruction not in sources.values():
            sources[f"{lineno}. {instruction}"] = []
        sources[f"{lineno}. {instruction}"].append(instruction)
    return sources


# ── disassembling functions ───────────────────────────────────────────────────

def get_function_argspec(fn) -> inspect.FullArgSpec:
    return inspect.getfullargspec(fn)


def get_function_annotations(fn) -> dict[str, type]:
    return fn.__annotations__


def get_function_defaults(fn) -> tuple[Any]:
    return fn.__defaults__


# ── CodeObjects ───────────────────────────────────────────────────────────────

def get_func_code(fn) -> types.CodeType:
    return fn.__code__


def get_func_co_varnames(fn) -> tuple[str]:
    return fn.__code__.co_varnames


def get_func_co_argcount(fn) -> int:
    return fn.__code__.co_argcount


def get_func_co_nlocals(fn) -> int:
   

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
