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


# ── ctypes & struct — low-level bit twiddling ──────────────────────────────────

class BitField:
    def __init__(self, width: int, offset: int) -> None:
        self.width = width
        self.offset = offset
        self.mask = ((1 << width) - 1) << offset

    def encode(self, val: int) -> int:
        assert isinstance(val, int)
        return (val << self.offset) & self.mask

    def decode(self, raw: int) -> int:
        return (raw >> self.offset) & self.mask


def bitfield(value: int, width: int, offset: int) -> BitField:
    return BitField(width, offset)

#: 2-bit field starting at byte offset 1
FOO_FIELD = bitfield(2, 1)
#: 5-bit field starting at byte offset 1
BAR_FIELD = bitfield(5, 1)

#: 4-byte field starting at byte offset 2
BAZ_FIELD = bitfield(4, 2)


def test_bitfields() -> None:
    assert FOO_FIELD.encode(7) == 0b0000_0111
    assert BAR_FIELD.decode(0b0000_0111) == 7
    assert BAZ_FIELD.decode(BAR_FIELD.encode(9)) == 9


# ── copyreg, marshal — pickle and serialization utilities ─────────────────────

def custom_pickle_reducer(obj: object) -> tuple[type[Any], object]:      # noqa: ANN401
    # this is the guts of the pickle protocol...
    return obj.__reduce_ex__("pickle_protocol")


def register_custom_pickler() -> None:
    copyreg.pickle(object, custom_pickle_reducer)


register_custom_pickler()
del custom_pickle_reducer       # make sure it's not available to other modules


def pickle_tester(payload: Any) -> Any:
    data = marshal.dumps((type(payload), payload))
    _, result = marshal.loads(data)
    assert result == payload
    return result


def pickle_marshal_tester(payload: Any) -> Any:
    data = marshal.dumps(payload)
    _, result = pickle.load(io.BytesIO(data))
    assert result == payload
    return result


# ── importlib machinery — dynamic imports, module metadata, etc. ──────────────

# The following two functions are taken    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

