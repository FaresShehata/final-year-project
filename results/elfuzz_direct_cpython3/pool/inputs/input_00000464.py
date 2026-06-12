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
"""

print(annotated_disassembly(lambda x, y: x + y))
assert annotated_disassembly(lambda x, y: x + y) == """
  3           0 LOAD_FAST                0 (x)
              3 LOAD_FAST                1 (y)
              6 BINARY_ADD
              7 RETURN_VALUE
"""


# ── Disassembling code objects ───────────────────────────────────────────────

class MyFunction:
    def __init__(self):
        self.func = lambda x: x + 1

    def __getattribute__(self, name):
        if name in {"func", "__dict__"}:
            return super().__getattribute__(name)

        return getattr(self.__self__.__dict__["func"], name)


my_func_inst = MyFunction()
dis.dis(my_func_inst.__getattribute__("func"))
assert my_func_inst.func.code is not None


# ── Code objects and their fields ─────────────────────────────────────────────

co = inspect.getfullargspec(MyFunction().func).code
# The 'arg' field can be accessed via the .co_argcount attribute.
assert co.co_argcount > 0
# The 'fname' field can be accessed via the .co_filename attribute.
assert isinstance(co.co_filename, ctypes.c_char_p)
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