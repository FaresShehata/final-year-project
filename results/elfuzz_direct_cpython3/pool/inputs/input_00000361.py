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
import sys
import timeit
import types
import weakref
import weakref as _weakref


class CustomModule:
    def __init__(self) -> None:
        self.__dict__["x"] = "custom module"


def main() -> int:
    # Seed 1 - Low-level Python: bytecode introspection, dis, code objects, ctypes,
    #           struct, array, memoryview, pickle, copyreg, marshal, importlib,
    #           sys internals, frame inspection, gc, tracemalloc, weakref, __slots__

    print("Seed 1 — Low-level Python: bytecode introspection, dis, code objects, ctypes, struct, array, "
          "memoryview, pickle, copyreg, marshal, importlib, sys internals, frame inspection, gc, tracemalloc, "
          "weakref, __slots__")

    # Bytecode introspection with dis
    print(dis.dis(compile("print('Hello World')", filename="foo.py", mode='exec')))
    print("\n" + "-" * 50)

    # Code objects
    foo_py_code_obj = compile("print('Hello World')", filename="foo.py", mode='exec')
    print(foo_py_code_obj.co_argcount)
    print(foo_py_code_obj.co_varnames)
    print(foo_py_code_obj.co_name)
    print(foo_py_code_obj.co_filename)
    print(foo_py_code_obj.co_firstlineno)
    print(foo_py_code_obj.co_flags & dis.CO_OPTIMIZED)
    print(foo_py_code_obj.co_flags & dis.CO_NEWLOCALS)
    print(foo_py_code_obj.co_consts[0].co_name)
    print("\n" + "-" * 50)

    # Ctypes
    foo_c_type = ctypes.c_char_p(b'Hello World')
    print(type(foo_c_type))  # <class 'ctypes.c_char_p'>
    print(foo_c_type.value)  # b'Hello World'
    print(ctypes.string_at(foo_c_type))
    print(ctypes.cast(foo_c_type, ctypes.POINTER(ctypes.c_byte)).contents.value)
    print(f'{len(foo_c_type)} bytes at {hex(id(foo_c_type))}')
    print(f'{ctypes.sizeof(foo_c_type)} bytes at {hex(id(foo_c_type))}')
    print(f'{ctypes.addressof(foo_c_type)} at {hex(id(foo_c_type))}')
    print(hex(id(foo_c_type.contents)))
