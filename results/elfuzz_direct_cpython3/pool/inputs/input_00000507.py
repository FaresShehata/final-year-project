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
    # print(dis.findlinestarts((lambda x: x)(fn)))
    # for instr in dis.get_instructions(fn):
        # print(f"{instr.offset:8} {instr.opname:<14}", end=" ")
        # if hasattr(instr, "arg"):
            # print(f"({instr.arg})")
        # else:
            # print()
    dis.dis(fn)
    return buf.getvalue()

def annotated_disasm(fn):
    print(annotated_disassembly(fn))

def annotated_disassemble(fn):
    print(dis.Bytecode(fn).dis())

print("\nBytecode introspection:")
annotated_disassemble(sys.getdlopenflags)


# ── Disassembling byte codes ──────────────────────────────────────────────────


def disassemble_bytecodes(obj):
    """
    Print the bytecodes of an object.

    :param obj: A callable or a type.
    """
    print("Disassembled bytecodes:")
    try:
        if inspect.isclass(obj):
            fn = getattr(obj(), "__init__", None)

        elif inspect.isfunction(obj):
            fn = obj
        else:
            raise TypeError(type(obj))

        # print(fn.__code__.co_code)
        dis.dis(fn)
    except AttributeError:
        print(f"No bytecodes found for {type(obj)}")

print("\nDisassembling bytecodes:")
disassemble_bytecodes(print)
disassemble_bytecodes(range)
disassemble_bytecodes(lambda x: x + 2)

# ── Code objects ──────────────────────────────────────────────────────────────


def show_code_object(code):
    """
    Show the `code` dictionary.

    :param code: The `code` dict from which to display contents.
    """
    print(textwrap.indent(
        f"""\
{code["argcount"]} arguments, {code["posonlyargcount"]} positional-only args, {code["kwonlyargcount"]} keyword only args,\
 {code["locals"]}, flags={hex(code["flags"])}, firstlineno={code["firstlineno"]},
 name="{code['co_name']}",
 argnames=({", ".join(f'"{i}"' for i in code["co_varnames"][:code["argcount"]] if i != "_")}),
 posargs=({", ".join(f'"{i}"' for i in code["co_varnames"][code["argcount"]:code["argcount"]+code["posonlyargcount"]] if i != "_