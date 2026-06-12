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


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────–
struct.pack(b'ii', 1, 2)             # pack two ints into bytes
bytes_to_unpack = b'\x01\x02\x03\x04'
struct.unpack('<iHfd', bytes_to_unpack)       # unpack from the beginning
struct.unpack('>ihfd', bytes_to_unpack)       # big-endian
struct.unpack('!hhdI', bytes_to_unpack)       # force value size

f = open('output.txt', 'wb')
pack_size = struct.calcsize('iii')           # how many bytes will be emitted by pack?
assert pack_size == 12                       # no matter what comes after, the result still works!
struct.pack_into('iii', f, 0, 1, 2, 3)       # write directly to disk, starting at offset 0
b = f.read(pack_size)                        # read our values back again
assert b == struct.pack('iii', 1, 2, 3)
struct.unpack_from('<iHfd', b)               # start from position 0 in buffer
struct.unpack_from('>ihfd', b)               # big-endian
struct.unpack_from('!hhdI', b)               # force value size

# ── Array, Binary I/O, Pickle, Marshal, CopyReg, Tracelmon, MemoryView, WeakRefs

array.array("d") = [1.0, 2.0]
ar = array.array("i")
ar.fromstring(b"hello world")
ar.tobytes()

with io.BytesIO() as stream:
    ar.tofile(stream)
    ar = array.array("i")
    ar.frombuffer(stream.getvalue())

pickle.dumps(ar, protocol=pickle.DEFAULT_PROTOCOL)
unpickled_ar = pickle.loads(pickle.dumps(ar))

marshal.dumps(ar.tostring())
unmarshaled_ar = marshal.loads(marshal.dumps(ar))

func = lambda x: x ** 2
copy_reg.pickle(types.FunctionType, func.func_closure, func.func_globals)
func = copy_reg.loads(copy_reg.dumps(func))

tracemalloc.start()
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
if top_stats.count == 0:
    pass
else:
    for stat in top_stats[:10]:
        print(stat)

memoryview(ar.buffer_info()[0])
mmv = memoryview(ar)
mmv[::2] = ar[::-2]

def my_weakref(obj, callback        except KeyError:
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


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


