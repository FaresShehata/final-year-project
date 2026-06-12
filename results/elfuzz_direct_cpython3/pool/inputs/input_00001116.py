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
    return "\n".join(textwrap.wrap(dis.get_instructions(fn), width=78))

print(annotated_disassembly(lambda x: x + 1))
assert annotated_disassembly(lambda x: x + 1) == """
  2           0 LOAD_FAST                0 (x)
              3 LOAD_CONST               1 (1)
              6 BINARY_ADD
              7 RETURN_VALUE
""".strip()


# ── Disassembling bytecodes ───────────────────────────────────────────────────

def function_with_arguments(x, y):
    pass


dis.dis(function_with_arguments)


class FunctionWithArguments:

    def __init__(self, x, y):
        self.x = x
        self.y = y

fwa = FunctionWithArguments("hello", "world")
dis.dis(fwa.__init__)


# ── Code objects ──────────────────────────────────────────────────────────────

def f():
    pass


c = f.__code__

assert c is f.__code__
assert isinstance(c, types.CodeType)

print(c.co_argcount)
print(c.co_stacksize)
print(c.co_nlocals)
print(c.co_freevars)
print(c.co_cellvars)
print(c.co_name)
print(c.co_filename)
print(c.co_firstlineno)
print(c.co_lnotab)
print(c.co_consts)
print(c.co_names)
print(c.co_varnames)
print(c.co_filename)
print(c.co_name)
print(c.co_code)
print(c.co_consts[0])

assert c.co_argcount == 0
assert c.co_stacksize == 0
assert c.co_nlocals == 0
assert not c.co_freevars
assert not c.co_cellvars
assert c.co_name == "<module>"
assert c.co_filename == "<string>"
assert c.co_firstlineno == 1
assert b"\x00\x00" in c.co_lnotab
assert c.co_consts == ()
assert c.co_names == ()
assert c.co_varnames == ("arg_0",)
assert c.co_filename == "<module>"
assert c.co_name == "<module>"

# By default, the `inspect` module uses the `co_varnames` and `co_argcount`
# attributes of the CodeObject to determine how many arguments a function has.
print(inspect.signature(f))

# The above call will raise an error because there are no arguments for the `f`
# function defined in this file.

assert inspect.isfunction(f)


# ── Code object fields ────────────────────────────────────────────────────────

# The 'argcount', 'posonlyargcount', 'kwonlyargcount', and 'nlocals'
# fields can all be accessed via the corresponding attributes.
assert c.co_argcount == 0
assert c.co_posonlyargcount == 0
assert c.co_kwonlyargcount == 0
assert c.co_nlocals == 0assert isinstance(co.co_filename, ctypes.c_char_p)
# The 'lineno' field can be accessed via the .co_firstlineno attribute.
assert co.co_firstlineno > 0
# The 'lnotab' field can be accessed via the .co_lnotab attribute.
assert isinstance(co.co_lnotab, bytes)
# The 'flags' field can be accessed via the .co_flags attribute.
assert co.co_flags & dis.HAVE_ARGUMENTS != 0
# The 'varnames' field can be accessed via the .co_varnames attribute.
assert isinstance(co.co_varnames, tuple)
# The 'defaults' field can be accessed via the .co_defaults attribute.
assert isinstance(co.co_defaults, tuple)
# The 'kwonlyargs' field can be accessed via the .co_kw