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

    # 1.1. Bytecode introspection, dis, code object
    print(dis.dis(lambda x: x))
    print("\n")
    print(dis.dis(critical_loop))

    # 1.2. Code objects
    print(inspect.getsourcefile(__name__))
    print(inspect.getmodule(__name__))
    print(sys.modules[__name__].__spec__)
    print(sys.modules["builtins"].__spec__)

    critical_loop_code = sys._getframe().f_back.f_code
    print(critical_loop_code.co_name)
    print(critical_loop_code.co_filename)
    print(critical_loop_code.co_consts)
    print(critical_loop_code.co_varnames)
    print(critical_loop_code.co_firstlineno)
    print(critical_loop_code.co_lnotab)

    # 1.3. Ctypes, struct and array

    print(ctypes.c_int.from_address(id(critical_loop)))
    print(struct.calcsize('c'))
    print(array.array('i', [0]))
    print(memoryview(b'hello world'))

    # 1.4. Pickle, copyreg, marshal, importlib, sys internals, frame inspection, gc,
    #       tracemalloc, weakref, __slots__

    print(pickle.dumps(critical_loop, protocol=pickle.HIGHEST_PROTOCOL))
    print(marshal.dumps(critical_loop))
    print(importlib.machinery.MAGIC_NUMBER)
    print(marshal.loads(marshal.dumps(critical_loop)))

    print(gc.isenabled())
    print(tracemalloc.is_tracing())

    c = CriticalLoop()
    c.run()

    f = open(__file__, "rb")
    with open(__file__, "wb") as out_file:
        for chunk in iter(lambda: f.read(8192), b""):
            out_file.write(chunk)
    f.close()

    # 2. Frame inspection
    from dis import dis as disassemble_code

    f = open(__file__, "rb")
    with open(__file__, "wb") as out_file:
        for chunk in iter(lambda: f.read(8192), b""):
            out_file.write(chunk)
    f.close()


class CriticalLoop:
    """Example of how to run a critical loop."""
    def __init__(self):
        pass

    def run(self):
        while True:
            continue


# Seed 06 - Low-level Python: bytecode introspection, dis, code objects, ctypes, struct, arrayprint(f"clobbers:\t{chr(0)}
      \thex\t{\xa9}
      \tascii\t{'\a'}
      \tnewline\t{chrs[10]}
      \traw\t{{!s}}
      \tparens\t{((None), (lambda: None))}
      \tmultiline\t{
                    lambda:
                        exit()
                  }""")
    print(
        f"clobbers:\t{chr(0)}\thex\t{{{ord('\xa9')}}}\tascii\t{{{ord('\a')}}}\tnewline\t{chr(10)}}\traw\t{{{!s}}}"
        f"\tparens\t{(None,), (lambda: None)}}\tmultiline\t{{\n"
        f"\t\tlambda:"
        f"\texit()\n"
        f"}}"}
    print()

    a = array.array("i", [0] * 10)

    print(a.buffer_info())
    print(a.itemsize)
    print(a.nbytes)
    print(a.typecode)

    s = 'Hello World!'
