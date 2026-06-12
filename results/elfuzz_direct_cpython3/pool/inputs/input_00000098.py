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
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)


def rename_module(mod: types.ModuleType, old_name: str, new_name: str) -> None:
    """Change mod.__name__ and mod.__file__ if necessary.

    This is done by replacing the module's filename or dirname (depending on whether it's an egg).
    """
    new_filename = mod.__spec__.origin.replace(old_name, new_name).rstrip(".pyw")
    if mod.__spec__.origin.endswith(new_filename):
        mod.__name__ = new_name      # don't need to touch this
        return
    # check for eggs
    if "/.egg-info/" in mod.__spec__.origin:
        idx = mod.__spec__.origin.rfind("/.egg-info/")
        assert idx > -1, "unexpected bad egg origin"
        prefix = mod.__spec__.origin[0:idx]
        new_spec = importlib.util.spec_from_file_location(new_name, new_filename)
        if not new_spec:
            raise ValueError(f"cannot create spec for {new_name} at {new_filename}")
        new_mod = importlib.util.module_from_spec(new_spec)
        new_spec.loader.exec_module(new_mod)
        new_mod.__name__ = new_name   # replace the module itself
        mod.__name__ = new_name       # replace the package containing it
        mod.__path__ = new_spec.submodule_search_locations  # update the path
    else:
        # load new module instance based on origin
        new_spec = importlib.util.spec_from_file_location(new_name, new_filename)
        if not new_spec:
            raise ValueError(f"cannot create spec for {new_name} at {new_filename}")
        new_mod = importlib.util.module_from_spec(new_spec)

        # replace globals in the new module with those from the old one
        load    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


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

