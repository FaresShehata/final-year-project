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
        total += i ** 2 - i
    return total


def test_bytecode_introspection():
    square = annotate(disassemble=square.__disassemble__)
    assert square(5) == 25
    assert annotated_disassembly(square) == """
      4           0 LOAD_FAST                0 (i)
                  3 LOAD_CONST               1 (2)
                  6 BINARY_POWER
                  7 LOAD_FAST                0 (i)
                 10 INPLACE_SUBTRACT
                 11 STORE_FAST               0 (i)

     10           14 LOAD_CONST               2 (0)
                 17 RETURN_VALUE"""


# ── Dis ───────────────────────────────────────────────────────────────────────

def annotate(
    fn: Callable[..., Any],
    *,
    disassemble: bool = True,
    show_code_object: bool = False,
) -> Callable[..., Any]:

    def wrapper(*args, **kwargs):
        print(">>>", fn.__qualname__, "<<<")
        if disassemble:
            print(disassemble_fn(fn))
        if show_code_object:
            print(show_code_obj(fn))
        result = fn(*args, **kwargs)
        print(result)
        return result

    return wrapper


def disassemble_fn(fn: Callable[..., Any]) -> str:

    def linebreak(codeobj: types.CodeType) -> str:
        lines_of_code = codeobj.co_code.count(bytes([ord("\n")]))
        max_line_length = 80 // (lines_of_code + 1)
        return "\n".join([
            line.ljust(max_line_length) for line in textwrap.wrap(
                "".join(chr(i) for i in codeobj.co_code),
                width=max_line_length,
                initial_indent="",
                subsequent_indent="   ",
            )
        ])

    return textwrap.indent(textwrap.dedent(inspect.getsource(fn)), prefix="│\t")


def show_code_obj(fn: Callable[..., Any]) -> str:
    return textwrap.indent(repr(inspect.getcode(fn)), prefix="│\t")


# ── Code Objects ───────────────────────────────────────────────────────────────

def annotate_code_objects(fn: Callable[..., Any], *, dump: bool = True):
    if dump:
        print(textwrap.indent(str_code_objects(fn), prefix="│\t"))
    else:
        print(textwrap.indent(repr_code_objects(fn), prefix="│\t"))


        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
