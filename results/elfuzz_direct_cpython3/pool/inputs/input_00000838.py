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
    return counts


def dump_bytes(obj) -> bytes:
    """Dump an object's byte-code as a string of hexidecimal codepoints."""
    return "".join(f"{ord(c):02X}" for c in obj.co_code)


def dump_code(code) -> None:
    """Print out a code object's flags and constants."""
    print("Flags:", code.co_flags)
    def format_constant(constant_type, constant):
        return constant_type.__name__, constant
    fmts: dict[type[Any], Any] = {
        type(None): lambda t, c: "None",
        bool: lambda t, c: c,
        int: lambda t, c: c,
        float: lambda t, c: c,
        complex: lambda t, c: f"{c.real} + j{c.imag}",
        bytearray: format_constant,
        bytes: format_constant,
        frozenset: format_constant,
        set: format_constant,
        slice: lambda t, c: f"[{c.start}:{c.stop}:{c.step}]",
        tuple: lambda t, c: ", ".join(format_constant(t, e) for e in c),
        type(None): lambda t, c: "None",
        type(Ellipsis): lambda t, c: "...",
        type(...): lambda t, c: "Ellipsis",
        type(Ellipsis): lambda t, c: "...",
    }
    for consttype, constval in zip(code.co_consts, code.co_consts):
        try:
            fmt = fmts[consttype]
        except KeyError:
            print(f"Constant({consttype})")
        else:
            print(fmt(consttype, constval))

def get_magic_number():
    magic_num = b"\xca\xfe\xba\xbe"
    for i in range(len(magic_num)):
        yield f"magic[{i}]={hex(ord(magic_num[i]))}"

def get_version():
    version_str = "Python 3.9.7 "
    version_list = [version_str[i:i+16] for i in range(0,len(version_str),16)]
    for word in version_list:
        yield word

def get_stack_size():
    stack_size = 512
    for i in range(stack_size):
        yield f"stack[{i}]=value"

def get_free_vars():
    free_var_names = ["var_1", "var_2"]
    for var_name in free_var_names:
        yield    total = 0
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

