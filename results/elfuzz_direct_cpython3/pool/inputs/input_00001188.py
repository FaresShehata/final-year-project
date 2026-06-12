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
        assert isinstance(a, str)
        assert isinstance(b, str)
        assert isinstance(c, str)
        assert five.__code__.co_code == (
            "\x97\x18\x03\xf3\x02\xa6\x03\xfe\x02\xf3\x02\xb3\x03"
            "\xf3\x02\xc3\x03\x5f@\x02"
        )
        assert five.__code__.co_consts == (None, a, b, c, five)
        assert five.__code__.co_filename == "<module>"
        assert five.__code__.co_name == "five"
        assert five.__code__.co_varnames == ("x", "y", "z")
        assert five.__code__.co_firstlineno == 1
        assert five.__code__.co_lnotab == (
            b"\xff\xff"
        )  # The string contains the source line number for each instruction.
        assert five.__code__.co_flags == 0x0000
        assert five.__code__.co_freevars == ()
        assert five.__code__.co_cellvars == ()

    def test_disassemble_opcode(self) -> None:
        """
        https://docs.python.org/3/library/dis.html#opcode-constants
        https://docs.python.org/3/library/dis.html#opcode-PUSH_NULL
        https://github.com/python/cpython/blob/v3.10.0/Lib/dis.py#L44-L46
        """
        opname = dis.opname[dis.opcodes.OPCODES.index(0)]
        assert opname == "POP_TOP"

    def test_disassemble_block1(self) -> None:
        """
        https://github.com/python/cpython/blob/v3.10.0/Lib/dis.py#L293-L310
        """
        co = compile(
            "print('hello')\nreturn\nraise Exception()", "<string>", "exec