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
    while n > 0 and n < 2**31 - 1:
        total += n
        n >>= 1
    return total


def count_hot_path_calls(fn) -> dict[int, int]:
    def _count_hot_path_calls(*args, **kwds):    # type: ignore[no-untyped-def]
        for i in range(5):
            hot_path(i)

    func_code = fn.__code__
    module = func_code.co_filename.split(".py")[0]

    env = {
        "hot_path": hot_path,
        "__file__": f"{module}.py",
        "__name__": "__main__",
        "__package__": "",
        "__spec__": None,
    }
    with (sys.modules["__main__"] as main_module):    # type: ignore[attr-defined]
        exec("from __main__ import hot_path")
        del main_module.hot_path
    with (
        types.CodeType(
            func_code.co_argcount,
            func_code.co_kwonlyargcount,
            func_code.co_nlocals,
            func_code.co_stacksize,
            func_code.co_flags,
            b"",
            func_code.co_code,
            func_code.co_consts,
            func_code.co_names,
            func_code.co_varnames,
            env,
            func_code.co_filename,
            func_code.co_name,
            func_code.co_firstlineno,
            func_code.co_lnotab,
        ) as new_func_code
    ):
        with (
            types.FunctionType(new_func_code, globals()) as wrapped_fn:
                wrapped_fn.__defaults__ = tuple(range(6))
                count = 0
                while count < 1_000_000:
                    _count_hot_path_calls()
                    count += 1
        )
    return {i: count // 6 for i in range(1, 7)}


def count_function_calls(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        if instr.opname == "CALL_FUNCTION":
            name = instr.argval.rsplit(".", maxsplit=1)[0].strip("'\"")
            counts[name] = counts.get(name, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def annotate_call_count(call_counts) -> dict[str, int]:
    min_val = sum