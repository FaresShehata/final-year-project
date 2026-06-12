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
    opcodes = {}
    for i in range(dis.HIGHEST_INSTRUCTION_NUMBER):
        try:
            opcode_name = dis.opname[i]
        except KeyError:
            continue
        else:
            opcodes[opcode_name] = opcodes.setdefault(opcode_name, 0) + 1
    return opcodes


def get_instructions(fn) -> list[tuple[int, str, tuple]]:
    instructions = []
    for i in range(dis.HIGHEST_INSTRUCTION_NUMBER):
        try:
            opcode_name = dis.opname[i]
        except KeyError:
            continue
        instruction_offset = dis.op_offset(i)
        instruction_arg = dis.oparg(i)
        instructions.append((instruction_offset, opcode_name, instruction_arg))
    return instructions


disassembled_python_function = annotated_disassembly(lambda x: x * x)


print("\nPython byte-code disassembled:")
for line in disassembled_python_function.splitlines():
    print(line)

counted_opcodes = count_opcodes(lambda x: x * x)

print("\nCount of each opcode:")
for name, num in counted_opcodes.items():
    print(f"{name}: {num}")

instructions = get_instructions(lambda x: x * x)

print("\nInstructions:")
for offset, opcode_name, arg in instructions:
    print(f"\t{offset}:\t\t{opcode_name}{'' if arg == 0 else ' ' + hex(arg)}")


# ── Disassembly of C functions ─────────────────────────────────────────────────
#
# Note that this wouldn’t be possible on an interpreter because the C library has
# its own virtual machine. In fact, it’s even more interesting than the Python VM
# because it’s written in C.
#
# The Cython project aims to make writing high-performance extensions to Python as
# easy as writing normal Python.

# import ctypes
# import math

# libm = ctypes.CDLL(None)
# libm.sin.restype = ctypes.c_double
# libm.cos.restype = ctypes.c_double
# libm.tan.restype = ctypes.c_double

# def sin(x):
#     return libm.sin(ctypes.c_double(x))


# class MyCFunction(ctypes.Structure):
#     _fields_ = [
#         ("sin", ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)),
#         ("cos", ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_double)),
#         ("tan", ctypes.CFUNCTYPE(ctypes.c_doublefrom __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


# ── Code objects ──────────────────────────────────────────────────────────────

python_code_object = compile("print('Hello world!')", "<string>", "exec")

print("\nCode object:\n\n", python_code_object)

print("\nSource code:\n\n", python_code_object.co_names)


# ── Using the built-in functions to debug your code ──────────────────────────

def superfluous_print():
    print("Hello, world!")

with open("superfluous_debug.log", "w") as file:
    execute(superfluous_print(), file)


# ── Info about the standard library modules ───────────────────────────────────

print("\nStandard library information:")

def module_info(module: types.ModuleType) -> None:
    print(
        f"Name:\t\t{module.__name__}\n"
        f"File:\t\t{module.__file__}\n"
        f"Doc:\t\t{getattr(module, '__doc__', '')}"
    )

modules = {
    name: getattr(sys.modules, name) for name in dir(sys.modules)
}

for module in sorted(modules.values()):
    module_info(module)


def is_module(name: str) -> bool:
    """Is the given string the name of a module?"""
    try:
        module = sys.modules[name]
    except KeyError:
        return False
    else:
        return isinstance(module, types.ModuleType)


is_module("sys")
is_module("os.path.abspath")


# ── Information about classes, methods, properties, attributes, variables ──

r"""
There are two main ways to retrieve information about classes, methods, etc:

- Reflection is a way to dynamically query information at run-time.
- Descriptors are a way to implement metadata, such as docstrings, type hints,
  default values, and other useful information. This can also be used by tooling
  like IDEs, documentation generators, linters, and formatters.
"""


# ── Descriptors ──────────────────────────────────────────────────────────────


class BookkeepingDescriptor:
    """
    Used to track bookkeeping information associated with a descriptor.
    """

    def __init__(self):
        self.access_count = 0
        self.read_only = False
        self.initial_value = None

    def get(self, instance: Any | None) -> Any:
        """Get a descriptor attribute when reading from an instance."""
        self.access_count += 1from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount
    if not callable(arity):
        raise ValueError(
            "Invalid number of arguments passed to `curry`. "
            "The wrapped argument has an invalid value.",
        )
    
    def wrapper(*args: A):
        if len(args) == arity:
            return fn(*args)
        
        def inner(*inner_args: A):
            return wrapper(*(list(args) + list(inner_args)))
        
        return inner
    
    return wrapper

@functools.lru_cache(maxsize=None)
def memoize(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @functools.wraps(func)
    def wrapper(*arg: Any):
        if arg in wrapper.cache:
            return wrapper.cache[arg]
        else:
            result = func(arg)
            wrapper.cache[arg] = result
            return result
    
    wrapper.cache = {}
    return wrapper


# ── Partial application and composition with lambdas ────────────────────────

def compose_with_lambda(composition_list: list[Callable]):
    return (
        lambda *args: reduce(operator.compose, composition_list)(*args)
    )


# ── Trampoline functions ───────────────────────────────────────────────────

def trampoline(f: Callable[[Any], Generator[Any, None, Any]]) -> Any:
    """Run the generator as many times as needed to return a value."""
    while True:
        try:
            result = next(f())
        except StopIteration as e:
            return e.value

def _summands_generator(numbers: Iterable[int]) -> Generator[int, None, int]:
    """Calculate the summands from a range of numbers."""
    total = 0
    for number in numbers:
        yield number
        total += number
    return total

def is_even(number: int) -> bool:
    return number % 2 == 0

def is_odd(number: int) -> bool:
    return number % 2 != 0

def even_or_odd_trampoline(numbers: Iterable[int]) -> bool:
    """Check if any number in a sequence is odd using a trampoline."""
    generator = _summands_generator(numbers)
    return trampoline((lambda: (yield from generator))()) or False


if __name__ == "__main__":
    # ── Lambda-calculus church encodings ─────────────────────────────────────
    print(church_to_int(int_to_church(4)))