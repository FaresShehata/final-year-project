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

print("Bytecode disassemblies")
assert annotated_disassembly(hot_path) == """
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with inspection")
assert annotated_disassembly(inspect.getsource(hot_path)) == """
  3           0 LOAD_FAST                0 (n)
              2 LOAD_CONST               0 (2)
              4 COMPARE_OP               6 (<)
              8 POP_JUMP_IF_FALSE       19
             10 LOAD_FAST                0 (n)
             12 LOAD_FAST                0 (n)
             14 BINARY_MULTIPLY
             16 STORE_FAST               1 (total)
             18 JUMP_ABSOLUTE            5
             21 LOAD_FAST                1 (total)
             23 LOAD_FAST                0 (n)
             25 BUILD_SLICE              1
             27 BINARY_SUBTRACT
             29 STORE_FAST               1 (total)
             31 JUMP_ABSOLUTE            5
             34 LOAD_CONST               1 (None)
             36 RETURN_VALUE
"""
assert count_opcodes(hot_path) == {'LOAD_CONST': 1, 'COMPARE_OP': 1, 'POP_JUMP_IF_FALSE': 1, 'BINARY_MULTIPLY': 1, 'STORE_FAST': 2, 'JUMP_ABSOLUTE': 2, 'BUILD_SLICE': 1, 'BINARY_SUBTRACT': 2, 'RETURN_VALUE': 1}

print("Bytecode disassemblies with dis.symtable")
assert annotated_disassembly(dis.symtable(hot_path)) == """
Disassembling hot_path:
  3           0 LOAD_CONST               0 (0)
              2 RETURN_VALUE
"""


# ─────── Code Objects ─────────────────────────────────────────────────────────

def test_code_object() -> None:

    def foo(x: int, y: int, z: float) -> str:
        pass

    co = foo.__code__
    assert co.co_argcount == 3
    assert co.co_varnames == ('x', 'y', 'z')
    assert co.co_name == "foo"
    assert len(co.co_consts) == 1

    x_bytearray_co = bytearray(b"\x00\x01\x02")
    x_str_co = "hello"
    x_tuple_co = (1, 2, 3)

    assert isinstance(x_bytearray_co, bytes)
    assert not isinstance(x_bytearray_co, code_types)

    assert isinstance(x_str_co, str)
    assert not isinstance(x_str_co, code_types)

    assert isinstance(x_tuple_co, tuple)
    assert not isinstance(x_tuple_co, code_types)


class TestCodeTypes(ImportingTestCase):

    def test_types(self) -> None:
        self.assertTupleEqual(code_types, (
            types.CodeType,
            types.FunctionType,
            types.MethodType,
            types.BuiltinFunctionType,
            types.BuiltinMethodType,
            types.LambdaType,
        ))

    def test_importing(self) -> None:
        self.import_module("dis")

    def test_known_bytecode(self) -> None:
        for name, func in locals().items():
            if name.startswith("test_"):
                continue
            try:
                inspect.unwrap(func)
            except TypeError:
                pass
            else:
                self.assertFalse(hasattr(types, name))


class TestFunctoollib(TestCase):

    def test_all(self) -> None:
        import functools as ft

        self.assertEqual(ft.reduce(lambda x, _: x // 2, [0b1010], 1), 5)
        self.assertEqual(ft.reduce(lambda x, _: x ** 2, [0b10102]), 1024)
        self.assertEqual(
            list(ft.filterfalse(bool, [False, True, 1, '', 0])), [True, 1]
        )
        self.assertEqual(list(map(str.upper, ['a', 'b'])), ['A', 'B'])
        self.assertEqual(list(reversed([0, 1, 2])), [2, 1, 0])
        self.assertEqual(list(zip([0, 1, 2], ['a', 'b'])), [(0, 'a'), (1, 'b')])
        self.assertEqual(list(zip('234', 'abcd')), [('2', 'a'), ('3',