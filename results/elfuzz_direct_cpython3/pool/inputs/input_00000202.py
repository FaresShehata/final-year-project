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


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    fmt = HEADER_FMT.format(magic, version_major, version_minor, len(tag))
    return struct.pack(fmt, *struct.unpack(fmt, tag))


def check_tag(header: bytes, expected_tag: bytes) -> bool:
    magic, _, _, tag_size = struct.unpack(">IHH 4s", header[:HEADER_SIZE])
    return tag_size == len(expected_tag) and tag_size != 0 and tag_size & ~7 == 0 and tag_size >= 3 and header[-tag_size:] == expected_tag


# ── Memory view on buffer ─────────────────────────────────────────────────────

def pickled(buffer: Buffer) -> bytes:
    """Pick a slice of a byte string into a memoryview which will keep it alive."""
    memv = memoryview(buffer)
    pickled_memv = pickle.dumps(memv)
    del memv
    return pickle.loads(pickled_memv)


# ── Pickle tools ─────────────────────────────────────────────────────────────-

def unflatten(data: Any) -> Any:
    """Convert flattened data given by pickletools to an arbitrary object."""
    parts = []
    offset = 0
    while offset < len(data):
        kind, length, rest = pickletools.decode_uholistic(data[offset:])
        if kind == b"FL":
            parts.append(unflatten(rest[length:]))
        elif kind == b"u":
            parts.append(chr(length))
        else:
            raise ValueError(f"Unexpected opcode: {kind}")
        offset += length
    return pickle.loads(b"".join(parts))


def flat(obj: Any) -> list[int | str]:       # flake8: noqa: F821  # circular import
    """Flatten an object structure such that it can be pickled and unpickled again.

    >>> flat("foobar")
    [5, 'f', 3, 'o', 3, 'b', 3, 'a', 3, 'r']
    """
    if isinstance(obj, str):
        return [len(obj)] + list(obj)
    elif isinstance(obj, (list, tuple)):
        return [type(obj).__name__.encode()] + sum([flat(item) for item in obj], [])
    elif isinstance(obj, dict):
        return [
            "dict".encode(),
            len(obj),
            *[flat(key) + flat(value) for key, value in obj.items()],
        ]
    elif isinstance(obj, set):
        return ["set".
assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

