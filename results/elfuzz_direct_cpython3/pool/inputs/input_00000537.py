"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import enum
import inspect
import itertools as it
import math
import os
import platform
import random
import re
import struct
import sys
import timeit
import types
import typesupport
import typing
import weakref

import numpy as np
import numpy.typing as npt

try:
    import tracemalloc
except ImportError:
    tracemalloc = False

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterable, Iterator, List, Tuple, TypeVar

T = TypeVar("T")


class Color(enum.Enum):
    RED      = "\x1b[31m"
    GREEN    = "\x1b[32m"
    YELLOW   = "\x1b[33m"
    BLUE     = "\x1b[34m"
    MAGENTA  = "\x1b[35m"
    CYAN     = "\x1b[36m"
    WHITE    = "\x1b[37m"
    RESET    = "\x1b[0m"

    @classmethod
    def echo(cls, msg: str, color: Color | None = None) -> str:
        if color is None:
            return cls.WHITE.value + msg + cls.RESET.value
        elif isinstance(color, Color):
            return color.value + msg + cls.RESET.value
        raise TypeError(f"'color' must be an instance of {Color} or None")

    @classmethod
    def fadeout(cls, msg: str, color: Color, duration_s: float) -> str:
        time.sleep(duration_s / 2)

        start_color = cls.color.value.strip("\x1b")
        end_color = f"\x1b[{duration_s}s{cls.RESET.value}"

        print(start_color + msg + end_color, end="", flush=True)
        time.sleep(duration_s / 2)

        print(cls.RESET.value, end="", flush=False)


@types_supports(int)
def f_round(value: T, ndigits: int = 0) -> T:
    return round(float(value), ndigits=ndigits)


def get_random_seed(seed=None) -> int:
    """Get a deterministic (and reproducible) seed for use with random.random()."""
    if seed is None:
        seed = int(time.time())
    assert seed >= 0, "seed must be non-negative"
    return seed


# ── low-level Python: bytecode intros
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


# ── dis and bytecodes ─────────────────────────────────────────────────────────

def show_opcodes(fn: types.FunctionType, count: int = 1000) -> None:
    """Print the first 'count' op codes of the function's bytecode."""
    dis.disassemble(fn, count=count)


def show_and_compare(opcodes_1: bytes, opcodes_2: bytes) -> None:
    diff = opcodes_1.decode("ascii") != opcodes_2.decode("ascii")
    print(diff)
    if not diff:  # pragma: no cover
        return

    label_width = max(len(name) for name in opcodes_1.splitlines())

    def _print(line: str) -> None:
        s_line = line.ljust(label_width, " ")
        print(s_line.rstrip(), end="")
        for part in line.split():
            if part.isdigit():  # Assume it's a register number.
                print(Color.BLUE.echo(f"({part}) "), end="")  # pylint: disable=W0511
            else:
                print(part, end="")
        print()

    print()
    for line in opcodes_1.splitlines():
        _print(line)
    print()
    for line in opcodes_2.splitlines():
        _print(line)


def show_opcode(line_number: int) -> None:
    """
    Print the opcode for the specified line, along with its operands.

    Example:

    $ python -c 'def foo(): pass'
    1           0 LOAD_CONST               0 (<code object <module> at 0x...>)
                3 LOAD_CONST               1 ('foo')
                6 DISCARD              ...
                9 MAKE_FUNCTION            ...
               10 LOAD_CONST               0 (None)
               13 RETURN_VALUE
    >>>
    >>> show_opcode(1)
    1: LOAD_CONST 0 (<code object <module> at 0x...)
       NAME: <module>
       LOAD_NAME: foo
       ...
    """

    class OpcodePrinter(dis.Bytecode):  # type: ignore[misc]
        def format(self, offset: int) -> str:
            try:
                insn = self.code.co_code[offset:]
                name = dis.opname[self.code.co_code[offset]]
                oplineno = next(i for i, v in enumerate(insn) if v <= ord(b":"))
                operand = insn[:oplin