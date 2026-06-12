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
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__ or ()
    )
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


class AnnotatedCodeObject(types.CodeType):
    def __repr__(self):
        name = getattr(self, "co_name", "<anonymous>")
        return f"<AnnotatedCodeObject {name}>"

    def replace(self, *, co_name=None, **kwds):
        # Python 3.8+. If you've written your own replacement function that
        # doesn't support the same arguments as CodeType.replace(), it's
        # probably safest to just re-create all of the attributes yourself.
        kwds["co_name"] = co_name or self.co_name
        return super().replace(**kwds)


def make_code_object(name: str, argcount=1, nlocals=3, stacksize=8, flags=0):
    # Make an arbitrary code object we can annotate later.
    return AnnotatedCodeObject(
        compile(f"def foo(x): pass\nprint({argcount})", "", "exec"), name=name
    )


def modify_code_object(obj: types.CodeType | AnnotatedCodeObject) -> None:
    # Modify existing code objects by altering their constants and names. This
    # will change how the function is executed when it’s called; e.g., it may
    # not execute any more instructions than necessary.
    obj.co_consts[0] = ("This is the first constant.",)
    obj.co_names.append("bar")


def modify_code_object_and_clone(
    fn: types.FunctionType, name: str, new_name: str
) -> types.FunctionType:
    """Clone fn, then modify its code object."""

    modifiable = clone_with_name(fn, "__modifies__")
    code = modifiable.__code__
    modify_code_object(code)

    # The original function has been modified, but the resulting functions are
    # still one-to-one mappings between values (e.g., globals).
    cloned = clone_with_name(modifiable, new_name)
    assert cloned.__code__ != code
    assert cloned.__code__ == modifiable.__code__

    return cloned


def modify_code_object_and_replace(
    fn: types.FunctionType, name: str, new_name: str
) -> types.FunctionType:
    """Replace fn's code object with another one."""

    # We don't have to use clone_with_name here because the result function
    # isn't bound to a name