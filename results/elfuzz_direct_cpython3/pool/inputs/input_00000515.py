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

    # Low-level Python: bytecode introspection, dis, code objects, ctypes, struct, array, memoryview, pickle, copyreg, marshal, importlib, sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
    print("\nLow-level Python: bytecode introspection, dis, code objects, ctypes, struct, array, memoryview, pickle, copyreg, marshal, importlib, sys internals, frame inspection, gc, tracemalloc, weakref, __slots__")

    # Code Objects
    # https://docs.python.org/3/reference/import.html#importing-a-source-file-as-a-module
    # https://docs.python.org/3/library/codecs.html#codecs.open
    # https://docs.python.org/3/library/functions.html#open
    # https://docs.python.org/3/library/io.html#io.BytesIO
    # https://stackoverflow.com/questions/207558/how-to-convert-between-bytes-and-hexadecimal-in-python
    # https://www.geeksforgeeks.org/converting-string-to-byte-array-using-python/
    #
    # https://docs.python.org/3/library/os.html?highlight=system%20command#os.system
    # https://www.tutorialspoint.com/python/os_system.htm
    print(f"\ndecorator: {inspect.getsource(dis.dis)}\n")
    dis.dis(lambda x: x + 1)
    print()

    print(f"module name: {sys._getframe().f_code.co_filename}")
    print(f"line number: {sys._getframe().f_lineno}")
    print(f"name: {sys._getframe().f_globals['__name__']}")
    print(f"file: {sys._getframe().f_code.co_filename}")

    print(f"arg count: {dis.code_info(lambda x: x + 1)[1]}")
    print(f"local vars: {len(inspect.stack()[1][0].f_locals.keys())}")
    print(f"filename: {inspect.stack()[1][1]}")
    print(f"linenumber: {inspect.stack()[1][2]}")

    with open(__file__, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if len(line.split(",")) > 1:
                continue
            print(line)

    with