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
        'LOAD_NAME': 3,    'LOAD_STRING': 1,     'MAKE_FUNCTION': 1,
        'EXTENDED_ARG': 1, 'POP_JUMP_IF_FALSE': 1, 'FOR_ITER': 1,
        'CALL_FUNCTION_KW': 1, 'CALL_FUNCTION_EX': 1, 'LOAD_ATTR': 2,
        'BINARY_SUBSCR': 1, 'IMPORT_FROM': 1, 'LOAD_CLASSDEREF': 1,
        'LOAD_CONST': 1,   'STORE_NAME': 1,      'LOAD_BUILD_CLASS': 1,
        'LOAD_METHOD': 1,  'STORE_NAME': 1,      'COPY':     fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

