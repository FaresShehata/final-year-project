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
    This is useful when you want to monkeypatch modules without changing their
    original contents.
    """
    mod.__name__ = new_name
    mod.__spec__.name = new_name


def patch_importer(path: str, loader: importlib.abc.Loader) -> None:
    """Use another Loader subclass to load files at path."""
    sys.path_importer_cache[path] = loader


def patch_submodule(module: types.ModuleType, submodule: str | bytes) -> None:
    """Create a new submodule with the same attributes as module.submodule."""
    spec = importlib.util.find_spec(submodule, package=module.__name__)
    assert spec
    setattr(module, submodule, importlib.util.module_from_spec(spec))


# ── Ctypes ────────────────────────────────────────────────────────────────────

def carray(n: int, dtype: type[float | int]) -> array.array[float | int]:
    """Return an array whose items are initialized by pointing to a memory block
    allocated with ctypes.c_array(). The caller must ensure that the array size
    does not exceed the number of elements specified by the ctypes size parameter.
    """
    return array.array(dtype, (ctypes.c_float() for _ in range(n)))


# ── Struct ────────────────────────────────────────────────────────────────────

def pack(fmt: str, /, *args) -> bytearray:
    """Pack multiple values according to fmt into a buffer and return the results
    as a bytes-like object.

    Supported formats:
      * c — signed char
      * b — signed char
      * h — short
      * H — unsigned short
      * i — int
      * I — unsigned int
      * l — long
      * L — unsigned long long — long long
      * q — long long
      * f — float
      * d — double
      * P — void pointer (this can also be used like "p")
      * s — string (byte string; can contain '\0')
      * S — unicode string (string; can't contain '\0')

    Note: If the format string ends with "l" or "q", only 64-bit integers are
    supported on Windows when using the Python interpreter compiled as x32.
    """
    return struct.pack(fmt, *args)


def unpack(fmt: str, data: bytes) -> tuple[Any]:
    """Unpack values according to fmt from the beginning of the buffer data."""
    return struct.unpack(fmt, data[: struct.calcsize(fmt)])


def unpack_into(fmt: str, buffer: bytearray, offset: int = 0) -> tuple[int]:
    """Unpack values according to fmt from the beginning of the buffer data and
    store them in the corresponding positions starting at buffer[offset].
    """
    return struct.unpack_into(fmt, buffer, offset)[: len(fmt) // 2]


# ── Array ─────────────────────────────────────────────────────────────────────

def append(array: array.array, element: int) -> None:
    array.extend((element,) * 5)


# ── Memory view ───────────────────────────────────────────────────────────────

def show_memory_view(mv: memoryview) -> str:
    """Print information about mv to a string."""
    result = []
    result.append(f"type={type(mv).__name__}")
    result.append(f"length={mv.nbytes}")
    result.append(f"itemsize={mv.itemsize}")
    result.append(f"readonly={repr(mv.readonly)}")
    result.append(f"contiguous={repr(mv.contiguous)}")
    result.append(f"format={repr(mv.format)}")
    result.append("elements:")
    for index, item in enumerate(mv):
        result.append(f"{index}: {item!r}")
    return "\n".join(result)


# ── Pickle, copyreg, marshal ──────────────────────────────────────────────────

def call_pickler(pickleable: Any) -> None:
    """Call pickle.dumps() and pickle.loads() directly."""
    pickle.dump(pickleable)
    pickle.load(io.BytesIO(pickle.dumps(pickleable)))


def call_unpickler(unpickleable: Any) ->    try:
        yield f.read()
    finally:
        f.close()


with open_file("./test.txt", mode="r") as file:
    print(file)


@contextlib.contextmanager
def suppress(*exceptions):
    """Suppress any exception that matches the given exceptions."""
    try:
        yield
    except exceptions:
        pass


@contextlib.contextmanager
def redirect_stdout(stream):
    """Redirect stdout to another stream while within this context."""
    old_stream = sys.stdout
