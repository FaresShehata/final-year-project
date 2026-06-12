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

# ── dis - decodes bytecodes from a .pyc or .pyo file ──────────────────────────

PYTHON_BYTECODES = {
    'dis': dis.dis,
    'load_const': load_const,
    'load_name': load_name,
    'build_class': build_class,
}

for name, fn in PYTHON_BYTECODES.items():
    print(f"Disassembling {name}:")
    print(annotated_disassembly(fn))
    print()


# ── Code Objects ──────────────────────────────────────────────────────────────

SOURCE_CODE = textwrap.dedent("""
    def foo(x):
        x += 1
    del x
    """).strip()
print("\nCode object:")
CO = compile(SOURCE_CODE, filename="<demo>", mode="exec")

print(CO.co_filename)
print(CO.co_firstlineno)
print(CO.co_consts)
print(CO.co_names)
print(CO.co_varnames)

if CO.co_argcount == 0:
    print("No positional arguments.")
elif CO.co_argcount == 1:
    print("One positional argument:", CO.co_varnames[0])
else:
    print("Multiple positional arguments:")

args_spec = CO.co_argflags
for arg_idx in range(CO.co_argcount):
    if args_spec[arg_idx]:
        print("\t", CO.co_varnames[arg_idx])


# ── ctypes - allows you to create and manipulate C data structures ────────────

class IntArrayType(ctypes.Structure):
    _fields_ = [("value", ctypes.c_int)]

arr = IntArrayType(value=5)
assert arr.value == 5


# ── struct - lets you pack arbitrary binary data into structured formats ───────

packer = struct.Struct("<ii")  # little-endian signed integers 2 bytes each
packed_data = packer.pack(7, 8)  # packed data (bytes-like)

unpacker = struct.Struct(">ih")  # big-endian unsigned short and an integer
unpacked_data = unpacker.unpack(packed_data)  # unpacked data


# ── array - creates arrays of fixed-size items that are indexed by numbers ────

arr = array.array('i', [1, 2, 3])
arr.append(-99)
del(arr[2])
assert arr[-1] == -99

arr = array.array('d')
arr.extend((log10(1e-6), log10(1)))
assert arr.tobytes().hex() == "3ff0000000000000 3f31000000000000"


# ── memoryview - provides low-level access to typed memory buffers ────────────

memory_view = memoryview(array.array('b', b'abc'))
assert memory_view[:].tobytes() == b'\x61\x62\x63'
memory_view[:] = b'def'

del(memory_view)
del memview

# ── pickle and unpickle

class MyClass:
    def __init__(self, n: int) -> None:
        self.n = n
    def __repr__(self) -> str:
        return f"MyClass(n={self.n})"

obj = MyClass(42)

pickle_str = pickle.dumps(obj, protocol=pickle.DEFAULT_PROTOCOL)
other_obj = pickle.loads(pickle_str)

assert other_obj.n == obj.n

# ── copyreg - register a custom constructor for pickling and unpickling ─────from logging import Logger
from math import isclose, log10
from operator import add, mul
from pathlib import Path
from queue import Queue
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Final,
    Generic,
    Iterator,
    Literal,
    NamedTuple,
    NoReturn,
    Optional,
    Protocol,
    Tuple,
    Union,
)
from unittest.mock import patch, call

import pytest
import rich.console
import rich.traceback
from pytest_regressions.file_regression import FileRegressionFixture

try:
    from _pytest.reports import TestReport
except ImportError:
    class TestReport(object):
        pass

try:
    from _pytest.outcomes import Failed
except ImportError:
    class Failed(Exception):
        def __str__(self) -> str:
            return self.args[0]


def test_concurracy():
    """Concurrency."""

    @dataclass(frozen=True)
    class Foo:
        i: int = 0

    # concurrent.futures.ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_1 = executor.submit(Foo.i.__add__, 2)
        future_2 = executor.submit(Foo.i.__add__, 3)

    assert future_1.result() == 2 + 2
    assert future_2.result() == 3 + 3

    # concurrent.futures.ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_1 = executor.submit(Foo.i.__add__, 2)
        future_2 = executor.submit(Foo.i.__add__, 3)

    assert future_1.result() == 2 + 2
    assert future_2.result() == 3 + 3


@pytest.mark.parametrize("cls", [int, float])
def test_literals(cls: type[Any]) -> None:
    """Literal."""
    assert cls(1) == 1
    assert cls(1) != 2
    assert cls(1) in {1}
    assert cls(1) not in {2}
    assert isinstance(cls(1), int)


def test_literal_iterables() -> None:
    """Literal iterables."""
    a = (1,)
    b = tuple([1])

    assert a == b
    assert a != set()
    assert a <= set()

    c = frozenset([1, 2, 3])
    d = frozenset({1, 2, 3})

    assert a == c
    assert a != d
    assert c <= d

    assert a < d

    e = {1: 1}

    assert a == e
    assert a