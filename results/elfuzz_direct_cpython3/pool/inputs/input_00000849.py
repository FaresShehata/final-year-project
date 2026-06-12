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
            total -= i * i * i
    return total


# ─── low-level Python: dis │ python ──────────────────────────────── • · 8.9. 2
def _dis_what_to_do(disassemble: bool, bytecodes: bool, labels: bool, opnames: bool) -> None:
    if disassemble:
        print(Color.RED.echo("Disassembling..."))

    if bytecodes:
        print(Color.GREEN.echo("Bytecode(s):"))
    if labels:
        print(Color.YELLOW.echo("Labels:"))
    if opnames:
        print(Color.BLUE.echo("Operation name(s):"))


def _dis_bytecode_assembly(bytecode: bytes, label: str = "") -> None:
    bytecode = bytecode.decode()

    parts = []
    comment_lines = []

    for line in bytecode.splitlines():
        if line.startswith("#"):
            comment_lines.append(line)
        else:
            parts.extend(re.findall(r"[^\d\s]+", line))

    instruction_names = {
        "NOP":       "No operation",
        "POP_TOP":   "Pop top item off stack",
        "ROT_TWO":   "Rotate items 2 places up the stack",
        "ROT_THREE": "Rotate items 3 places up the stack",
        "DUP_TOP":   "Duplicate top item on stack",
        "PRINT_EXPR":f"Print expression '{', '.format() and ')'",
        "LOAD_CONST":f"Load constant '{value}' into stack",
        "STORE_NAME":f"Store value onto local variable '{name}'",
        "LOAD_NAME": f"Load variable '{name}' onto stack",
        "RETURN_VALUE":"Return value to caller",
    }

    try:
        for part, instruction_name in zip(parts[:-1], parts[1:]):
            if instruction_name in instruction_names.keys():
                if label != "":
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>                    print(
                        f"{label}{part:<16}",
                        f"{' ' * (len(instruction_name) - 1)}",
                        instruction_name.capitalize(),
                    )
    except UnicodeDecodeError:
        pass

    print("\n".join(comment_lines))


def _dis_print_labels(disassembly: str) -> None:
    lines = disassembly.strip().splitlines()
