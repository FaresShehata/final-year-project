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
    char_array.fromlist(c_char_packed)

    # Now create a buffer that points to each array's underlying memory.
    int_view = memoryview(int_array)
    float_view = memoryview(float_array)
    double_view = memoryview(double_array)
    char_view = memoryview(char_array)

    print(f"{int_view.tobytes()=} ({type(int_view).__name__}<{hex(id(int_view))})")
    print(f"{float_view.tobytes()=} ({type(float_view).__name__}<{hex(id(float_view))})")
    print(f"{double_view.tobytes()=} ({type(double_view).__name__}<{hex(id(double_view))})")
    print(f"{char_view.tobytes()=} ({type(char_view).__name__}<{hex(id(char_view))})")

    # We can read/write this as though it were an ordinary bytes-like object!
    int_view[0] = b"\xff"
    print(f"{int_view.tobytes()=} ({type(int_view).__name__}<{hex(id(int_view))})")


# ── Pickling & unpickling ────────────────────────────────────────────────────

def pickling_examples() -> None:
    # For example, use a recursive function to demonstrate pickling support for
    # submodules and nested modules.
    def sub_module_example():
        """Pickling a submodule works just like it does for other modules."""
        import pickle
        import foo.bar.baz.quux
        submodule_serialized = pickle.dumps(foo.bar.baz.quux)
        module_deserialized = pickle.loads(submodule_serialized)
        assert isinstance(module_deserialized, foo.bar.baz.quux.Quux)


# ── Copying objects ───────────────────────────────────────────────────────────

def copy_reg_pickle_examples():
    """
    Demonstrates pickling and unpickling examples that use `copyreg.pickle`.
    """
    def foo_class_factory(*args):
        return FooClass(*args)

    @copyreg.pickle_unpickle
    class FooClass:
        def __init__(self, value):
            self.value = value

    @copyreg.pickle_unpickle
    class BarClass(FooClass):
        pass

    copy_reg_pickle_examples()

    # The above is equivalent to...
    copy_reg.register_instance_fallback(foo_class_factory, FooClass)


