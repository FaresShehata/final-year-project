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
import types
import traceback
import unittest
import weakref
import weakref.remainder as remainder_wrt_weakref


class Test(unittest.TestCase):
    def test_five(self) -> None:
        """https://docs.python.org/3/library/dis.html#dis.dis"""
        a = "a"
        b = "b"
        c = "c"
        five = lambda x, y, z: x + y * z
        code = five.__code__
        assert isinstance(a, str) and isinstance(b, str) and isinstance(c, str)
        assert len(code.co_varnames) == 2
        assert len(code.co_names) == 1
        assert code.co_nlocals == 5
        assert code.co_stacksize == 8
        assert code.co_flags == 960
        assert code.co_firstlineno == 1
        assert code.co_lnotab == b"\x00\x01\x00" if six.PY2 else b""
        assert code.co_freevars == ()
        assert code.co_cellvars == ("y",)

    def test_code_objects(self) -> None:
        """http://python-history.blogspot.com/2013/08/complete-guide-to-code-object.html"""
        code = compile("Hello World!", "<string>", "exec")
        self.assertEqual(type(code), types.CodeType)
        self.assertEqual(len(inspect.getargspec(code).args), 1)
        self.assertEqual(code.co_consts[0], "Hello World!")

    def test_importlib(self) -> None:
        """https://docs.python.org/3/library/importlib.html"""
        spec = importlib.util.spec_from_file_location(
            "example_module", "/path/to/example_module.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "function")
        assert isinstance(module.function, types.FunctionType)

    def test_sys_internals(self) -> None:
        """
        https://docs.python.org/3/c-api/intro.html#c.SYS_MAX_SIZE_T
        https://docs.python.org/3/c-api/memory.html#c.Py_ssize_t
        https://docs.python.org/3/c-api/object.html#c.PyObject
        """
        assert (sys.maxsize >> 32) >= 0xFFFFFFFF // 2
        assert sys.intern is getattr(sys, "_intern")

    def test_frame_inspection(self) -> None:
        """https://docs.python.org/3/reference/datamodel.html#the-standard-type-hierarchy"""
        # repr() of a Frame object contains the name of its type, which may be useful for debugging.
        class MyFrame(types.FrameType):
            pass
        f = MyFrame()
        print(f"{type(f)!r} {f}")
        assert f.f_back is None
        # The standard library module “inspect” provides functions to extract information from frames in various formats.
       