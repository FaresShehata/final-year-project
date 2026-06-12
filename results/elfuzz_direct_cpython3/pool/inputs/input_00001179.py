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
    def __repr__(self) -> str:
        return repr(self.val)


ct = MyCtypes(75)
print(ct.val)
assert ct.val == 75
ct.val = 99
assert ct.val == 99
del ct   # check we don't hold on to memory by reference
gc.collect()

# ── Struct, Array, MemoryView ────────────────────────────────────────────────

# https://docs.python.org/3/c-api/memoryblock.html#c.PyMemoryView_FromBuffer
memoryview_buffer = array.array(b"Hello, world!")
membv = memoryview(memoryview_buffer)

# https://docs.python.org/3/c-api/array.html#c.PyArray_SimpleNewFromData
pyarray = array.array(b"b", [ord(c) for c in bytearray(membv)])
pyarr = pyarray.view()

# https://docs.python.org/3/c-api/memory.html#c.PyMem_Malloc
memptr = ctypes.c_void_p.in_dll(sys._internal_gil_library, "PyMem_Malloc")(len(membv))
if memptr.value:
    mvmem = ctypes.cast(memptr, ctypes.POINTER(ctypes.c_char))
    ptrval = ctypes.string_at(mvmem)
    print(f"{ptrval=} {ptrval.decode()=}")
else:
    raise RuntimeError("allocation failed")

# ── Pickle, CopyReg, Marshal ─────────────────────────────────────────────────

# https://docs.python.org/3/library/pickletools.html
pickletools.dis(pickled_bytes)

with open("pickled_bytestream.bin", "wb") as fh:
    pickle.dump(object_to_dump, fh)

with open("pickled_file.txt", "w+") as fh:
    fh.write(pickle.dumps(object_to_dump))

with open("pickled_file.txt", "r") as fh:
    unpickled_object = pickle.loads(fh.read())

# https://docs.python.org/3/library/pickle.html
pickle.loads(pickle.dumps(obj))

parsed_pickle_repr = pickletools.disassembler(pickle.dumps(obj))[0].disassemble()
unparseable_repr = pickletools.unparse(pickle.dumps(obj)[2:-1])

# https://docs.python.org/3/library/pickletools.html#module-pickletools
pickletools.optimize(pickled_bytes)

# https://docs.python.org/3/library/pickle.html#pickle.Unpickler.dispatch
dispatch_dict: dict[str, Callable[[Any], Any]] = {
    "int": lambda x: x ** 2,
    "float": lambda x: -x,
}
with open("obj.pickle", "rb") as fh:
    unpickled_obj = pickle.load(fh, dispatch_dict)

# https://docs.python.org/3/library/pickletools# https://docs.python.org/3/library/struct.html
data = b"\x00\x12\x00\x1d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

