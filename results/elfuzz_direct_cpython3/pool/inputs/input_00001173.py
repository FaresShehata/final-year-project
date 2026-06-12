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

if False:
    from typing_extensions import TypedDict


def print_function_code_info():
    """Inspect the contents of a function's code object."""
    def sample_func():
        x = "Hello"
        y = [1, 2]
        z = {"a": 1}
        return x + str(y) + str(z)

    func = sample_func.__code__

    # Print out all attributes of the function's code object.
    for attr in dir(func):
        if not callable(getattr(func, attr)):
            print(f"func.{attr} = {getattr(func, attr)}")


def print_instruction_details(insn):
    """Print details about an instruction."""
    print()
    print("===")
    print("Instruction:", insn)
    print("Offset:", hex(insn.co_offset))
    print(
        f"{insn.opname} - {dis.opmap[insn.opname]}",
        end=" ",
    )
    print(
        f"\n{dis.opname}: {insns_to_str(instructions=insn.instructions)}"
    )
    print()


def instructions_to_str(instructions: list[tuple[str, int, int]] | None) -> str:
    """Convert list of (opname, arg, offset) tuples to string."""
    lines = []
    for op, arg, offset in instructions or []:
        line = f"{op:<25}{arg}"
        if len(line) > 78 and arg is not None:
            line += "\n" + (" " * 35) + f"{offset:>6d}"

        lines.append(line)

    return ", ".join(lines)


def print_disassemble(code_object):
    """Disassemble a compiled function."""
    print(dis.disassemble(code_object))


def inspect_frame_locals(frame):
    """Inspect local variables of a particular stack frame."""
    print()
    print("===")
    print("Frame locals:")
    print()
    for name, value in sorted(inspect.getlocalnames(frame)):
        print(f"name={name}, value={value}")

    for name, value in sorted(inspect.getlocals(frame)):
        print(f"name={name}, value={value}")


def get_source_lines(source_path):
    """Get source code lines given a filename/path."""
    with open(source_path, encoding="utf-8") as file_:
        lines = [
            lines.strip("\r\n").rstrip("\n") for lines in file_.readlines()
        ]

