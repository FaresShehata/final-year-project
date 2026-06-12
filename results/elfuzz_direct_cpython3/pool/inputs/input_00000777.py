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
    

def caller_info_extended(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        **caller_info(depth),
        "code":       frame.f_code,
        "f_globals":  frame.f_globals,
        "f_locals":   frame.f_locals,
        "f_builtins": frame.f_builtins,
    }


class PseudoFrame(object):

    def __init__(self, f_globals: dict[str, Any], f_locals: dict[str, Any]):
        self.f_globals = f_globals
        self.f_locals = f_locals

    @property
    def f_code(self) -> types.CodeType:
        raise NotImplementedError("Use `PseudoFrame.code` instead")

    @property
    def code(self) -> types.CodeType:
        return types.CodeType(
            self.f_code.co_argcount,
            self.f_code.co_kwonlyargcount,
            self.f_code.co_nlocals,
            self.f_code.co_stacksize,
            self.f_code.co_flags,
            b"",
            self.f_code.co_consts,
            self.f_code.co_names,
            self.f_code.co_varnames,
            self.f_globals["__name__"],
            "",
        )

    @property
    def f_trace(self) -> types.FrameType | None:
        raise NotImplementedError("Not implemented")


def inspect_frame(fobj: types.FrameType, n: int = 1) -> dict:
    frame = PseudoFrame(fobj.f_globals, fobj.f_locals)
    locals_ = [frame]
    for i in range(n - 1):
        frame = frame.f_back
        if frame is None:
            break
        locals_.append(PseudoFrame(frame.f_globals, frame.f_locals))
    return {"depth": n}
    
        
# ── Memory View ───────────────────────────────────────────────────────────────

def create_memory_view(obj: object, format_spec: str="") -> memoryview:
    length = len(format_spec) // 2
    shape = tuple(int(format_spec[i:i+2]) for i in range(0, length, 2))      # noqa: E741
    strides = tuple(-stride*item_size for item_size, stride in zip(shape[1:], shape[:-1]))[::-1]  # noqa: E741
    buffer = memoryview(obj).cast(format_spec)
    return memoryview(buffer).reshape(*shape).strided(strides)


def view_as_submatrix(mv: memoryview, y: int, x: int) -> memoryview:
    assert mv.shape[0] >= y + 1
    assert mv.shape[1] >= x + 1
    submv = memoryview(mv[y:y+1,x:x+1])
    submv.format = mv.format
    submv.itemsize = mv.itemsize
    return submv.reshape(submv.shape[0]*submv.shape[1])


def get_shape(mv: memoryview) -> tuple[int, ...]:
    result = []
    last_stride = mv.strides[-1]
    while True:
        res = (last_stride,)
        cur_mv = mv.reshape(res)
        next_last_stride = cur_mv.strides[-1]
        if next_last_stride != last_stride:
            result.insert(0, next_last_stride)
            last_stride = next_last_stride
        else:
            break
    return tuple(result)


def get_strides(mv: memoryview) -> tuple[int, ...]:
    return mv.strides


def get_format(mv: memoryview) -> str:
    return mv.format
    

def get_dtype(mv: memoryview) -> type[Any]:
    return mv.dtype
    
    
def get_typecode(mv: memoryview) -> str:
    return mv.typecode


# ── PyStruct ─────────────────────────────────────────────────