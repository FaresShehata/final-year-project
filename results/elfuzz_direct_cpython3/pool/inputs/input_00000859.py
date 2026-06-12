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
    if n == 1:
        return 2 * n - 3
    elif n < 10:
        return 16 * n ** n
    else:
        return n // 5


print(annotated_disassembly(hot_path))
print(dis.Bytecode(hot_path).dis())            # same result
print(count_opcodes(hot_path))


# ── Dis ───────────────────────────────────────────────────────────────────────

def sample_code() -> str:
    return """
    def hello(name):
      print(f"Hello {name}!")
"""


with open("sample.py", "w") as f:
    f.write(sample_code())


def describe_function(func_name):
    fname = func_name.replace("_", "")
    code_obj = compile(getattr(sys.modules["sample"], fname), filename="sample.py")
    return dis._format_function(code_obj)


for name in sorted(dir(dis)):
    val = getattr(dis, name)
    if not isinstance(val, type): continue
    if not (callable(val) and hasattr(val, "__code__")): continue
    if val.__name__.startswith("_"): continue
    if not isinstance(val.__code__, types.CodeType): continue
    if val.__code__.co_argcount != 1: continue
    if val.__code__.co_flags & dis.HAVE_ARGUMENTS == 0: continue
    yield name, describe_function(name)


# ── Code Objects ───────────────────────────────────────────────────────────────

class SampleCodeLoader(importlib.abc.SourceLoader):

    """A fake loader which loads a string of code."""

    def get_source(self, fullname):
        return 'print("hello world!")'


class MyModuleMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        assert name == 'MyModule'
        return super().__new__(cls, name, bases, namespace)

    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        return {'a': 1}


class MyModule(metaclass=MyModuleMeta):
    ...


my_module = importlib.import_module('my_module')


def describe_code_object(obj):
    class_name = obj.co_filename.split("/")[-1]
    try:
        code_class = importlib.import_module(class_name).__dict__[obj.co_name]
    except KeyError:
        code_class = "<unknown>"
    return f"{code_class}: {obj.co_firstlineno}"


try:
    with open("/does/not/exist/file.txt") as file: pass
except OSError as e:
    print(e)
else:
    print("The file was found.")



