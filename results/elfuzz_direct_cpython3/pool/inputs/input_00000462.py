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
    for op in dis.get_instructions(fn):
        opcode_name = op.opname.replace(" ", "_").replace("-", "_")
        if opcode_name not in counts:
            counts[opcode_name] = 1
        else:
            counts[opcode_name] += 1
    return counts


def my_count_opcodes(fn) -> list[Any]:
    # Disassembler can't be used here!
    buf = io.StringIO()
    with buf as buffer:
        print("#" * 5, "Disassembler", "#" * 5, file=buffer)
        dis.dis(fn, file=buffer)

        print("\n#" * 5, "Instruction count", "#" * 5, file=buffer)
        dis.tree(fn, file=buffer)

        print("\n#" * 5, "Bytecode details", "#" * 5, file=buffer)
        dis.show_code(fn, file=buffer)

        print("\n#" * 5, "Bytecode constants", "#" * 5, file=buffer)
        dis.show_consts(fn, file=buffer)

        print("\n#" * 5, "Bytecode names", "#" * 5, file=buffer)
        dis.show_names(fn, file=buffer)

        print("\n#" * 5, "Optimized bytecode", "#" * 5, file=buffer)
        dis.optimize(fn, file=buffer)


def main_bytecode_intro():
    from pprint import pformat

    # The following module is compiled to native machine code.
    import random

    print(annotated_disassembly(random.random))
    print(dis.as_pseudo_ops(count_opcodes(random.random)))
    print(pformat(count_opcodes(random.random)))


class MyRandom(object):
    def __init__(self, seed=None):
        self.seed = seed

    def random(self):
        pass


def main_my_random():
    r = MyRandom(seed=2)
    print(r.random())
    print(annotated_disassembly(MyRandom))


# ── Code objects ──────────────────────────────────────────────────────────────

def main_code_objects():
    import random

    print(type(random.randint))


def main_codes_dict():
    codes_dct = {}
    for name in dir(types):
        obj = getattr(types, name)
        if isinstance(obj, types.CodeType):
            key = f"{obj.co_filename}:{obj.co_firstlineno}"
            dct[key] = obj
    print