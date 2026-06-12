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
    a = n * (n - 3) // 2
    b = n ** 2
    c = (a + b) % n
    d = c + 1
    e = d * (d + 1) // 2
    return e


print(annotated_disassembly(hot_path))
print(count_opcodes(hot_path))

# ── Dis and code objects ──────────────────────────────────────────────────────

def generate_code(function_name: str | None = None, argcount: int = 0) -> types.CodeType:
    """Return an empty function object."""
    if function_name is not None:
        func = types.FunctionType(types.EmptyCode, globals(), name=function_name)
    else:
        func = types.FunctionType(types.EmptyCode, globals())
    co = func.__code__
    co.co_argcount = argcount
    co.co_flags |= dis.F_ANNOTATION
    co.co_consts = ()
    co.co_lnotab = ""
    co.co_names = ()
    co.co_varnames = ()
    return co


# ── Ctypes ────────────────────────────────────────────────────────────────────

libc = ctypes.CDLL(None)

for var in ["_SystemExit", "_Exception"]:
    print(f"ctypes.{var} is {getattr(libc, var)}")


# ── Struct ────────────────────────────────────────────────────────────────────

struct.pack()         # pack format string and bytes like 'i' and b'\x80\x00'
struct.unpack()       # unpack format string and bytes like 'i' and b'\x80\x00'
struct.calcsize()     # calculate size required for given format string
struct.Struct(format).pack_into()   # pack into buffer at offset using format
struct.Struct.format   # get the format string associated with a struct instance


# ── Array ────────────────────────────────────────────────────────────────────

pyarray = array.array('u', ['a', 'b', 'c'])
pyarray.tostring()                   # array-like object as bytes-like object
pyarray.tobytes()                    # same, but faster
pyarray.append(ord('d'))             # append byte as integer
pyarray.extend([ord('e'), ord('f')]) # append many integers
pyarray.frombytes(b'd\ne\f')         # construct array from bytes
pyarray.buffer_info()                # a pair containing the address and length of the underlying array object
pyarray.itemsize                     # the number of bytes needed to hold one element of this object
pyarray.typecode                     # the type code character used to create this array


# ── Memoryview ───────────────────────────────────────────────────────────────

memoryview(pyarray).cast('B').tolist()           # view as another object
memoryview(pyarray).readonly(False)               # make writable
memoryview(pyarray).reversed()                    # reversed view
memoryview(pyarray).toreadonly()                  # read-only view of itself
memoryview(pyarray)[0]                             # get first item
memory

def partial(fn: Callable[[A], B], /, *args: A) -> Callable[..., B]:
    """Partial application of an unary function.

    Args:
      fn: The function to be partially applied.
      args: The values to be bound as arguments to `fn`.
    Returns:
      A new function that is equivalent to `fn` with some of its arguments fixed.
    """
    if not callable(fn):
        raise TypeError("Expected a callable object.")

    def partial_fn(*other_args: A) -> B:
        combined_args = (*args, *other_args)
        if not all(isinstance(arg, arg_type) for arg, arg_type in zip(combined_args, fn.__annotations__["*"])):
            raise TypeError("Failed to apply partial application.")
        return fn(*combined_args)
    return partial_fn


# ── Trampoline ────────────────────────────────────────────────────────────────

class Return(Exception):
    """Return value used by trampoline."""

    def __init__(self, val: Any) -> None:
        super().__init__()
        self.val = val


def trampoline(fn: Callable) -> Callable:
    """Apply a trampolined function until it returns Return."""

    def wrapper(*args):
        while True:
            try:
                ret = fn(*args)
            except Return as e:
                return e.val
            if isinstance(ret, tuple) or hasattr(ret, "__iter__"):
                args = ret
            else:
                return ret

    return wrapper


# ── Serialisation ────────────────────────────────────────────────────────────

class Serialisable:
    """Define serialisation from/to dictionary."""

    def to_dict(self) -> dict[str, Any]:
        """Get the object's information as a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.value,
