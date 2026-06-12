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
            func_code.co_code,
            func_code.co_consts,
            func_code.co_names,
            func_code.co_varnames,
            func_code.co_filename,
            func_code.co_name,
            func_code.co_firstlineno,
            func_code.co_lnotab,
            func_code.co_freevars,
            func_code.co_cellvars,
        ) as new_func_code,
        types.FunctionType(new_func_code, globals(), name="fn", closure=None),
    ):
        fn = new_func_code
        with (types.ModuleType(module) as module_object):    # type: ignore[attr-defined]
            exec(_count_hot_path_calls.__code__.co_code, env)
            del module_object.fn
        return dict(sorted(env.items()))

# ── Disassembling a function’s bytecode ───────────────────────────────────────

def print_dis(func_or_codeobj: types.FunctionType | types.CodeType) -> None:
    buffer = io.BytesIO()
    dis.Bytecode(func_or_codeobj).dis(buffer)
    output_bytes = buffer.getvalue()[: buffer.tell()]
    buffer.close()

    print(textwrap.indent(output_bytes.decode(), " "*8))

# ── Code objects ───────────────────────────────────────────────────────────────

def code_repr(code_obj: types.CodeType) -> str:
    """Return repr of the given code object."""
    return f"<{type(code_obj).__name__} {code_obj.__code__!r}>"

def dump_bytecode(obj) -> None:
    if isinstance(obj, types.CodeType):
        print_repr(cached_repr=obj is not None)
    elif len(obj.func_code.co_code) <= 2000:
        print(f"CodeObject:\n{code_repr(obj.func_code)}\n")
        print_dis(obj.func_code)
    else:
        print(f"CodeObject:\n{code_repr(obj.func_code)}")

def print_repr(cached_repr=False) -> None:
    """Print the repr of a class or instance."""
    from collections.abc import Callable
    from dataclasses import is_dataclass

    if cached_repr:
        cls, inst = CachedReprClass(int), CachedReprInstance(int)
    else:
        cls, inst = ReprClass(int), ReprInstance(int)

    if isinstance(inst, (int, float)):
       