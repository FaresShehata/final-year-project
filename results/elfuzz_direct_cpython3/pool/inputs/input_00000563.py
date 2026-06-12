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


# ── Disassembler utility functions ────────────────────────────────────────────

def get_function_bytecode(fn) -> bytes:
    return marshal.dumps(dis.Bytecode(fn).to_bytes())


def pretty_marshal(data, indent=0) -> str:
    lines = pickletools.optimize(
        pickle.dumps(marshall.loads(data), protocol=-1))
    out = ""
    for line in lines:
        if isinstance(line, pickle.PickleableScalar):
            out += f"{' ' * indent}{line}\n"
        elif isinstance(line, pickle.ExtType):
            out += (
                f'{" " * indent}b{line.code} '
                f'type {hex(line.type)}\n'
            )
        else:
            out += f'{line}'
    return out.strip()


# ── Code object utilities ─────────────────────────────────────────────────────

def get_code_object(fn) -> types.CodeType:
    return fn.__code__

def dump_code_object(code) -> str:
    # NB: `dis` function doesn’t work with only the code object (it needs to be an
    #     instance of a code type).
    code_obj = types.CodeType(
        code.co_argcount,
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code,
        code.co_consts,
        code.co_names,
        code.co_varnames,
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab,
        code.co_freevars,
        code.co_cellvars,
    )
    return annotated_disassembly(code_obj)


# ── Low-level types and operations ────────────────────────────────────────────

def test_ctypes():
    return ctypes.c_int32(789456123) == ctypes.c_ulonglong(789456123)

def test_struct():
    x = array.array('i', [789456123])
    print(x.itemsize)
    
    return struct.unpack('>I', b'\x7\x8\x9\x4\x5\x6\x1\x2')[0]

def test_pickle():
    x = array.array('i', [789456123])

    data = pickle.dumps(x)
    print(pretty_marshal(data))

    y = pickle.loads(data)
    assert x.tolist() == y.tolist()

    z = bytearray([1, 2, 3])
    data = pickle.dumps(z)
    w = pickle.loads(data)
    assert list(w) == [1, 2, 3]


# ── Memoryview utilities ──────────────────────────────────────────────────────

def test_memoryview():
    x = array.array('u')
    x.frombytes(b"Hello world!\0")
    mv = memoryview(x)
    mv[1::2].readonly = True
    assert mv.readonly is True


# ── Pickle tools utility functions ────────────────────────────────────────────

def show_opcode_table(opcodes=None):
    """
    Display opcode table.
    """
   