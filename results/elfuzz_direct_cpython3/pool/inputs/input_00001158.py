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
    src = f"def adder({delta}):"
    compiled = compile(src, "<string>", "exec")
    globals_ = {"adder": lambda x: x}
    exec(compiled, globals_)
    # More robust than `make_function` since it allows us to specify the name.
    return clone_with_name(globals()["adder"], "add")


def get_code_object(name: str, arg_count: int, delta: int) -> types.CodeType:
    """Get the code object for a function defined via function definition syntax."""
    code = bytearray(f'"{name}".{arg_count}args').extend(code := b"\x01\x66\x97\x0b" +
                                                               b"i\x00\x00\x00" +
                                                               code[sizeof(code):])
    assert len(code) < 65536 - 102import importlib
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
    src = f"def adder({delta}):"
    compiled = compile(src, "<string>", "exec")
    globals_ = {"adder": lambda x: x}
    exec(compiled, globals_)
    # More robust than `make_function` since it allows us to specify the name.
    return clone_with_name(globals()["adder"], "add")


def get_code_object(name: str, arg_count: int, delta: int) -> types.CodeType:
    """Get the code object for a function defined via function definition syntax."""
    code = bytearray(f'"{name}".{arg_count}args').extend(code := b"\x01\x66\x97\x0b" +
                                                               b"i\x00\x00\x00" +
                                                               code[sizeof(code):])
    assert len(code) < 65536 - 102
    return types.CodeType(*inspect.signature
print()

with contextlib.redirect_stderr(None) as stderr:
    print(stderr.getvalue())
    print('Hello, World!')


# ── Numbers ABC ─────────────────────────────────────────────────────────────

assert isinstance(1.0 * 1.0, numbers.Real)
assert isinstance(-0.0, numbers.Number)
assert not isinstance(object(), numbers.Real)
assert not isinstance([], numbers.Number)

# ── Pathlib ─────────────────────────────────────────────────────────────────

pathlib.Path.cwd()
pathlib.PurePath("/usr/bin") / pathlib.PurePath("ls")


# ── Tempfile ───────────────────────────────────────────────────────────────

tempfile.gettempdir()
tempfile.TemporaryDirectory(prefix="my-unique-prefix", dir=tempfile.gettempdir())


# ── CSV ────────────────────────────────────────────────────────────────────

csv.writer(io.StringIO()).writerow(["foo", "bar"])
csv.reader(io.StringIO("spam,bagel\neggs,milk")).__next__()
list(csv.DictReader(io.StringIO("foobar\nbazquux")))



# ── Base64 ─────────────────────────────────────────────────────────────────

base64.b85decode(b"qQ==")
base64.b93decode(b"qQ==")
base64.b16decode("7E")
base64.b16encode(bytes(1))
base64.b16encode(bytes([1]))
base64.b16encode(bytearray(b"\x7e"))
base64.b16encode(memoryview(b"\x7e"))


# ── Hashlib ─────────────────────────────────────────────────────────────────

hashlib.md5(b"abc").hexdigest()


