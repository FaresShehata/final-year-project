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
print(f"{len(dis.get_instructions(hot_path)):} instructions")      # 6
print(hot_path.__code__.co_code)       # b'\x01\x00\x07_'
print(repr(hot_path.__code__))
print(hot_path.__code__.co_consts)     # (None, <built-in function div>,
                                        # None, 5, 9, 8, 3)

# ── Ctypes ────────────────────────────────────────────────────────────────────

this_module = sys.modules[__name__]
ctypes.CDLL.this_module = this_module
print(ctypes.CDLL(this_module).introduce_self())             # Hello world!

# ── Struct ────────────────────────────────────────────────────────────────────

struct.unpack("i", bytes.fromhex("01"))                     # (-2147483648,)
struct.pack(">ii", 1, 2)                                     # b'\\x01\\x00\\x00\\x00\\x02'

# ── Array ────────────────────────────────────────────────────────────────────

arr = array.array('l', [1, 2, 3])
print(arr.buffer_info())                                    # (140737488336096, 3)
print(arr.tolist())
copy = arr.copy()
print(copy is arr)                                          # True
print(copy == arr)                                          # False

# ── Memoryview ───────────────────────────────────────────────────────────────

membv = memoryview(bytearray(range(10)))
print(membv.tobytes())
mv_slice = membv[1:]
print(mvb_slice.tolist())

# ── Pickle ───────────────────────────────────────────────────────────────────

class MyClass:
    def __init__(self) -> None:
        self.value = 0

pickle.dumps(MyClass(), protocol=pickle.HIGHEST_PROTOCOL)

pickled_bytes = pickle.loads(b"\x80\x03c__main__\nMyClass\nq\x00)\x81q\x01."
                            "Q\x00\x85q\x02X\x04\x00\x00\x00valueq\x03K\x00\x86")

unpickled_obj = pickle.loads(pickled_bytes)
print(unpickled_obj.value)                                   # 0
print(type(unpickled_obj))