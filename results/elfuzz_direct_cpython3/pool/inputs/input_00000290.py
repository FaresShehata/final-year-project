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
    globs: dict = {}     # needed by exec() but not used elsewhere
    fn = compile(src, "<anon>", "exec")
    assert isinstance(fn, types.CodeType)
    # Unpack the compiled code into a place we can edit it
    co = fn.co_code.copy()
    opcode = bytes([ord(c) for c in dis.opname[fn.co_names.index("ADD")]])
    # Replace opcodes to add or subtract value delta
    co[co.find(opcode)] = ord("+") if delta > 0 else ord("-")
    co[co.find(opcode)+1] |= ord(delta & 63)      # mask out top bit
    # Create and run test function using edited bytecode
    delco = fn.co_consts[1]
    fn = types.FunctionType(co, globals(), "_adder", delco, None)
    return fn


# ── ctypes ───────────────────────────────────────────────────────────────────

class MyCtypes(ctypes.Structure):
    def __init__(self, val: int | float | complex) -> None:
        self.val = val
    def __repr__(self) -> str:
        return repr(self.val)


# ── struct ────────────────────────────────────────────────────────────────────

_my_struct_t = struct.Struct("!f")


# ── array ────────────────────────────────────────────────────────────────────

my_array = array.array("i", [99])


# ── MemoryView ───────────────────────────────────────────────────────────────

memory_view = memoryview(my_array)


# ── Pickle ──────────────────────────────────────────────────────────────────

def double(value: int | float) -> int | float:
    return value*2


double_pickled = pickle.dumps(double)

pickled_func = pickle.loads(double_pickled)
assert pickled_func(2) == 4


# ── CopyReg ──────────────────────────────────────────────────────────────────

# Register some functions via copy_reg
pickle.register_function(lambda v: True, "MyBool")
copyreg.pickle(types.FunctionType, lambda v: False, lambda v: None, proto=None)

# Check they were registered
copied_bool = pickle.dumps(True, protocol=pickle.HIGHEST_PROTOCOL)
copied_func = pickle.dumps(lambda: True, protocol=pickle.HIGHEST_PROTOCOL)
assert copied_bool.startswith(b"B:")
assert copied_func.startswith(b"F:")

# Check that custom registration works as