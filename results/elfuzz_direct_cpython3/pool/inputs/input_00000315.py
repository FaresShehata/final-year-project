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
    frames = []
    while True:
        try:
            frame = sys._getframe().f_back
        except ValueError:
            break
        frames.append(frame.f_code.co_name)
    return frames


def depth_probe_stack_info() -> list[dict[str, Any]]:
    frames = []
    while True:
        try:
            frame = sys._getframe().f_back
        except ValueError:
            break
        info = {
            "filename": frame.f_code.co_filename,
            "function": frame.f_code.co_name,
            "lineno": frame.f_lineno,
            "locals": frame.f_locals,
        }
        frames.append(info)

    return frames[::-1]


# ── GC and tracemalloc ───────────────────────────────────────────────────────-

def show_garbage():
    print("Garbage:")
    for obj_ref in gc.garbage:
        print(obj_ref)


def show_traces():
    traces = tracemalloc.take_snapshot()
    print(f"{len(traces)} snapshots taken.")
    print(tracemalloc.display(traces))
    print("Current snapshot:")
    current_sample = traces.get_record_by_id(sys.tracemalloc.get_ref_count())
    print(current_sample.traceback.format())


# ── Weakrefs and slots ────────────────────────────────────────────────────────

class StructuredObject:

    __slots__ = ["x"]

    def __init__(self, x):
        self.x = x


class UnstructuredObject:

    def __init__(self, x):
        self.x = x


def run_weakref_test():
    struct_obj = StructuredObject(5)
    unstruct_obj = UnstructuredObject(3)
    weak_struct = weakref.ref(struct_obj)
    weak_unstruct = weakref.ref(unstruct_obj)

    assert weak_struct() is struct_obj
    assert weak_unstruct() is None

    del struct_obj
    del unstruct_obj

    assert weak_struct() is None
    assert weak_unstruct() is None


# ── Pickle and copyreg ────────────────────────────────────────────────────────

def test_copy_reg():
    class Foo:
        pass

    pickle.dumps(Foo)
    foo_type = type(Foo())

    pickled_foo = pickle.dumps(foo_type)
    unpickled_foo = pickle.loads(pickled_foo)

    assert unpickled_foo.type is foo_type
    assert unpickled_foo is not
# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
