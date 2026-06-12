"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)
from typing_extensions import ParamSpec, Concatenate, TypeAlias


def seed_05() -> None:

    # → 1. Threadsafe datastructures

    print("1. Threadsafe datastructures")

    # Python has two main thread-safe collections: `threading.Lock`-synchronized
    # dicts and `threading.RLock`-synchronized dicts (named after the lock they
    # use). *In this exercise*, we'll implement our own thread-safe dictionary.

    class ThreadSafeDict(dict):
        _lock: threading.Lock = threading.Lock()

        def __getitem__(self, key: object) -> object:
            with self._lock:
                return super().__getitem__(key)

        def __setitem__(self, key: object, value: object) -> None:
            with self._lock:
                super().__setitem__(key, value)

    a = ThreadSafeDict({"a": 1})
    b = ThreadSafeDict(
        {
            "b": {"c": [3, 2], "d": {"e": 4}},
            "f": 5,
        }
    )

    assert a["a"] == 1
    a["a"] = 42
    assert a["a"] == 42
    del a["a"]
    assert not ("a" in a)

    assert b["b"]["c"][1] == 2
    b["b"]["c"].append(99)
    assert b["b"]["c"][-1] == 99
    assert b["b"]["c"] == [3, 2, 99]

    assert repr(a) == "{...}"
    assert repr(b) == "{...}"

    # → 2. String parsing

    print("\n2. String parsing")

    # We've seen that strings are immutable, but sometimes you might want to be
    # able to modify individual characters or words within them. This is where
    # the `string` module comes into play!

    print("\nThe `string` module:")
    print(dir(string))

    # The `string` module contains many constants that represent sequences of
    # common string content. For example, `string.ascii_letters` contains all
    # lowercase and uppercase letters, which can be used to generate random
    # passwords that do not contain non-alphanumeric characters.

    print('\n\nThe `textwrap` module:')
    print(textwrap.dedent(inspect.getsource(textwrap.wrap)))

    # It provides functions for wrapping text, e.g., breaking long lines at
    # word boundaries so that lines don't exceed a certain length. By default,
    # it uses tabs to break lines between columns, but you can adjust the width
    # parameter to alter this behavior.

    print('A full list of formatting options:\n', dir(tokenize))   # Note: not available in pyodide!
    print(dir(ast))

    # You can use the `tokenize` submodule's `untokenize()` function to reverse
    # the tokenization process. This function takes a sequence of tokens and
    # returns a string representing the original source code.

    # The `ast` submodule allows you to parse string literals into abstract
    # syntax trees (AST). The `literal_eval()` method extracts values from
    # expressions without evaluating any operations. To see what happens when
    # you apply `literal_eval()` to a malformed expression like `'1 + '2'`,
    # you can refer to the documentation for `ast.literal_eval`. If you see the
    # following output, it means that there was no exception raised by your
    # string literal evaluation:

    try:
        print(ast.literal_eval("'hello world'")
              )             # <--- This will cause an error here.
    except SyntaxError:
        print("There were unclosed quotes.")
    except ValueError:
        print("We saw multiple equal operators.")

    # The `ast.unparse()` method takes an AST node and converts it back to
    # string form, according to the grammar defined by the PEG parser.
    # Unfortunately, you wouldn't usually need to call it directly because
    # the `eval()` function does it automatically before executing the
    #Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
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


# ── Memory view & array manipulation ──────────────────────────────────────────

def arrays_and_memory_views() -> None:
    """Demonstrate how to create arrays and memory views of arbitrary types."""
    # Define some data using the standard C types we know about...
    c_int_packed = [-1, -2]
    c_float_packed = [5.5e-6, 9.7]
    c_double_packed = [math.pi, math.e]
    c_char_packed = ["a", "\x00"]

    # ...and use struct.pack to pack them into arrays.
    int_array = array.array("i")
    int_array.fromlist(c_int_packed)

    float_array = array.array("f")
    float_array.fromlist(c_float_packed)

    double_array = array.array("d")
    double_array.fromlist(c_double_packed)

    char_array = array.array("c")
    char_array.frombytes(bytes(c_char_packed))

    # Construct memory views on these arrays...
    int_view = memoryview(int_array)
    float_view = memoryview(float_array)
    double_view = memoryview(double_array)
    char_view = memoryview(char_array)

    print("<int>:", repr(int_view.tobytes()))
    print("<float>:", repr(float_view.tobytes()))
    print("<double>:", repr(double_view.tobytes()))
    print("<char>:", repr(char_view.tobytes()))

    # ...and use struct.unpack to unpack them back.
    print("<int>: ", end="")
    print(*struct.unpack(f">{len(int_array)}i", int_view))
    print("<float>: ", end="")
    print(*struct.unpack(f">{len(float_array)}f", float_view))
    print("<double>: ", end="")
    print(*struct.unpack(f">{len(double_array)}d", double_view))
    print("<char>: ", end="")
    print(*struct.unpack(f">{len(char_array)}c", char_view))


# ── Copying vs pickling ───────────────────────────────────────────────────────

def copy_and_pickle(obj) -> tuple[Any, bytes, dict[str, Any]]:
    """Copy an object and pickle it for future inspection.

    Return: obj itself, its binary representation, and a map of ids that changed.
    """
    ref = weakref.ref(obj)
    copied_obj = copy.deepcopy(ref())
