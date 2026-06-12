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

print(dis.dis(hot_path))
print(f"{len(dis.get_instructions(hot_path)):} instructions")

disassemble_obj = dis.Bytecode(hot_path).disassemble()
for line in disassemble_obj.split("\n"):
    print(line)

# ── Ctypes ────────────────────────────────────────────────────────────────────

ctypes.c_int(-1)
ctypes.c_float(float("nan"))
ctypes.c_double(float("inf"))

# ── Struct ────────────────────────────────────────────────────────────────────

# struct.pack('i', ...): pack ints to bytes or vice versa
# struct.unpack('i', ...): unpack the bytes into an int
# struct.calcsize(): calculate size of packed data based on format string

struct.pack("i", 123456789)
struct.pack(">ii", 12345, 98765)
struct.unpack_from("<hh", b"abcefg")
struct.unpack_from(">hhh", b"abcdABCEFGH", offset=1)

# ── Array ─────────────────────────────────────────────────────────────────────

array.array("h", [1, 2, 3])
array.array("I", range(10))     # signed integer typecasted to unsigned
array.array("c", b"hello world")
array.array("u", b"h\N{COMBINING MACRON}\N{COMBINING ACUTE ACCENT}")
array.array("B", bytearray(range(256)))
array.array("b", [1])

# ── Memoryview ────────────────────────────────────────────────────────────────

memoryview(array.array("h", [-1]))
memoryview(array.array("I", range(10)), offset=1)
memoryview(array.array("c", b"Hello"), itemsize=2)

mview = memoryview(array.array("h", [1, 2, 3]))      # create view
print(mview.tobytes())
print(mview.tolist())
mview[0] = 42
mview.cast("B")[:]                            # cast view as bytes
mview.view(np.int32)[:]                       # view memoryview as NumPy ndarray
mview.flags.writeable                         # set flags for write access
mview.obj                                    # get object that created view

# ── Pickle ───────────────────────────────────────────────────────────────────

pickle.dumps(MyClass(1))
pickle.loads(pickle.dumps(MyClass(1)))

print(pickletools.dis(pickle.dumps(MyClass(1))))
print(pickletools.optimize(pickle.dumps(MyClass(1))))

with open("my_class.pickle", "wb") as f:       # pickling to file
    pickle.dump(MyClass(1), f)

with open("my_class.pickle", "rb") as f:       # unpickling from file
    my_class = pickle.load(f)

del MyClass; del my_class                     # cleanup after ourselves


# ── Importlib ─────────────────────────────────────────────────────────────────

spec = importlib.util.spec_from_file_location(
    'module_name',
    '/path/to/module.py'
)
if spec is not None:
    module = importlib.util.module_from_spec(spec)
else:
    raise ValueError("Module not found.")

sys.meta_path.append(module.__spec__)

print(importlib.import_module('module_name'))

# ── Sys internals ────────────────────────────────────────────────────────────<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>
# ── Copyreg ───────────────────────────────────────────────────────────────────

class MyClass:
    def __init__(self, value: int | float) -> None:
        self.value = value
    
    @classmethod
