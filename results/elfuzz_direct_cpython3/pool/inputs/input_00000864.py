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
    op_codes_count = {}
    for line in annotated_disassembly(fn).split("\n"):
        if not line.startswith(" "):
            continue
        opcode, operands = line.split(None, 1)[0], line[1:].strip()
        op_codes_count.setdefault(opcode, 0)
        op_codes_count[opcode] += 1
    return op_codes_count


# ── dis ───────────────────────────────────────────────────────────────────────

def test_opcode_counts():
    assert count_opcodes(dis.dis(int.__init__)) == {
        'POP_TOP': 5,     'LOAD_CONST': 6,      'RETURN_VALUE': 1,
        'STORE_NAME': 1,  'CALL_FUNCTION': 2,   'BUILD_CONST_KEY_MAP': 1,
        'LOAD_METHOD': 1, 'COMPARE_OP': 1,      'JUMP_IF_TRUE_OR_POP': 2,
        'SETUP_WITH': 1,  'WITH_CLEANUP': 1,    'PUSH_NULL': 1,
        'RETURN_VALUE': 1, 'YIELD_FROM': 1,     'RAISE_VARARGS': 1,
        'END_FINALLY': 1, 'EXEC_STMT': 1,       'LOAD_ATTR': 1,
        'UNPACK_SEQUENCE': 1,  'IMPORT_NAME': 1, 'IMPORT_STAR': 1,
        'GLOBAL': 1,       'STORE_FAST': 1,      'DELETE_FAST': 1,
        'STORE_NAME': 1,   'DELETE_NAME': 2,     'LOAD_GLOBAL': 1,
        'LOAD_DEREF': 1,   'STORE_DEREF': 1,     'LOAD_CLOSURE': 1,
        'POP_JUMP_IF_FALSE': 3,   'JUMP_FORWARD': 1,    'JUMP_ABSOLUTE': 1,
        'JUMP_BACKWARD': 1,         'FOR_ITER': 1,      'EXTENDED_ARG': 1,
        'SETUP_LOOP': 1,             'SETUP_EXCEPT': 1,  'SETUP_FINALLY': 1,
        }

# ── code object ───────────────────────────────────────────────────────────────

def get_code_object_of_a_function(func):
    # TODO This is the only way we know how to find out what's inside a function.
    # Should be able to work with any callable too?
    func_code_object = func.__code__
    print(f"func_name={func.__name__} func_code_object={func_code_object}")


def test_get_code_object_of_a_function():
    def foo():
        pass
    get_code_object_of_a_function(foo)

# ── ctypes ────────────────────────────────────────────────────────────────────

class CtypesTest:

    @staticmethod
    def test_create_struct():

        class Person(ctypes.Structure):

            _fields_ = [("age", ctypes.c_int),
                        ("name", ctypes.c_char_p)]

        p = Person(age=99, name="Bob")
        print(p.age, p.name)
        p.age = 100
        p.name = b"Cory"
        print(p.age, p.name.decode())

    @staticmethod
    def test_create_array():

        class BytesArray(ctypes.Array):

            _type_ = ctypes.c_byte
            _length_ = 8

        ba = BytesArray(b"\x01\x02\x03")
        print(ba)

    @staticmethod
    def test_create_union():

        class PersonUnion(ctypes.Union):

            _fields_ = [("int_age", ctypes.c_int),
                        ("bytes_age", BytesArray)]

        p = PersonUnion()
        p.int_age = -99
        print(p.bytes_age)

    @staticmethod
    def test_create_enumeration():

        class WeekdayEnum(ctypes.Enum):
            MONDAY = 1
            TUESDAY = 2
            WEDNESDAY = 3
            THURSDAY = 4
            FRIDAY = 5
            SATURDAY = 6
           