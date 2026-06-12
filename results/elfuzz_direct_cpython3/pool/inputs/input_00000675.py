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
    src = f"def adder({delta}):"
    compiled = compile(src, "<string>", "exec")
    globals_ = {"adder": lambda x: x}
    exec(compiled, globals_)
    # More robust than `make_function` since it allows us to specify the name.
    return clone_with_name(globals()["adder"], "add")


def get_code_object(name: str, arg_count: int, delta: int) -> types.CodeType:
    """Get the code object for a function defined via function definition syntax."""
    code = bytearray(f'"{name}".{arg_count}args').extend(code := b"\x01\x66\x97\x0b" +
                                                               b"i\x00\x00\x00" +
                                                               code[sizeof(code):])
    assert len(code) < 65536 - 1024, "Python's maximum line size is too small."
    code.extend(b"\x01\x00\x00\x00" + delta.to_bytes(4, byteorder="little"))
    return code


def switch_to_cython(fn: types.FunctionType) -> types.FunctionType:
    """Switch a function from PEP 380 mode to C extension mode.

    This does not extend the lifetime of the underlying function's module.

    ref: https://docs.python.org/3/library/dis.html?highlight=function%20definition#opcode-cpdef
    """

    # --- Extract PEP 380 metadata ---
    PEP_380_MAGIC_NUMBER = 414456
    magic_number = fn.co_filename.startswith("<pep380>")
    metadata = magic_number >> 15 << 15  # first two bytes are always zeros

    # --- Switch PEP 380 mode on/off in meta-data and emit new bytecode ---
    metadata ^= (PEP_380_MAGIC_NUMBER ^ metadata) & (
        # this will be zero when off, nonzero when on
        ~magic_number & PEP_380_MAGIC_NUMBER
    )

    # --- Construct an updated code object ---
    new_co = fn.__code__.replace(metadata=metadata)

    # --- Create a new function w/ the same closure as the original one ---
    new_globals = fn.__globals__.copy()
    new_closure = tuple((c.cell_contents,) for c in fn.__closure__)
    new_fn = types.Function

async def sleep(seconds: float | int) -> None:
    await asyncio.sleep(float(seconds))


def make_random_string(n: int | None = None) -> str:
    """
    Generate a string of length n filled with random lowercase letters.
    """
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n or 5))


def first_non_none(*args: T | None | None) -> T | None:
    try:
        return next(filter(None, args))
    except StopIteration:
        return None


def last_non_none(*args: T | None | None) -> Optional[T]:
    try:
        return next(reversed(filter(None, args)))
    except StopIteration:
        return None


def weighted_choice(choices: dict[V, float]) -> V:
    total_weight = sum(c.weight for c in choices.values