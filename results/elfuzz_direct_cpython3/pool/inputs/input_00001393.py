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
            func_code.co_filename,
            func_code.co_name,
            func_code.co_firstlineno,
            func_code.co_lnotab,
            func_code.co_freevars,
            func_code.co_cellvars,
        ) as new_func_code,
        types.FunctionType(new_func_code, globals(), fn.__code__.co_flags) as fn_new,
    ):
        fn_new.__globals__.update(env)
        fn_new.__closure__ = tuple()

        counts: dict[int, int] = {}
        for i in range(100):
            fn_new(*fn.__code__.co_varnames[: fn.__code__.co_argcount])
            counts[i | ((i & 2) << 1)] = counts.get(i | ((i & 2) << 1), 0) + 1
        del fn_new
    return dict(sorted(counts.items()))


def annotate_bytecode(func: types.FunctionType) -> str:
    sig = inspect.signature(func)
    body = ""
    for name, param in sig.parameters.items():
        if isinstance(param.annotation, types.FunctionType):
            opnames = count_opcodes(param.annotation)
            body += f"op_{param.name}:\n"
            body += "op_" * max(opnames.values()) + "\n\n"
    return textwrap.dedent(
        f"""\
        def {func.__name__}{body}
        """
    )


def print_bytecode(func: types.FunctionType):
    print(dis.Bytecode(func))


def print_bytecode_as_text(func: types.FunctionType):
    print(textwrap.indent(annotate_bytecode(func), "    "))


def print_bytecode_and_count_calls(func: types.FunctionType):
    sig = inspect.signature(func)
    body = ""
    for name, param in sig.parameters.items():
        if isinstance(param.annotation, types.FunctionType):
            opnames = count_hot_path_calls(param.annotation)[0]
            body += f"op_{param.name}: {len(opnames)}\n"
    print(f"\n{sig}\n{''.join(body)}")


# ───── Disassembling code from an object ──────────────────────────────────────

dis_obj = dis.Bytecode(hot_path).dis()
print(dis_obj)


# ───── Code objects ──────────────────────────────────────────────────────────

functools_code = types.CodeType(
    0,           # argcount