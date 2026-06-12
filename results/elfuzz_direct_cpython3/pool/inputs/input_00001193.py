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
    while n > 0 and n < 2**31 - 1:
        total += n
        n >>= 1
    return total


def count_hot_path_calls(fn) -> dict[int, int]:
    def _count_hot_path_calls(*args, **kwds):    # type: ignore[no-untyped-def]
        for i in range(5):
            hot_path(i)

    func_code = fn.__code__
    module = func_code.co_filename.split(".py")[0]

    env = {
        "hot_path": hot_path,
        "__file__": f"{module}.py",
        "__name__": "__main__",
        "__package__": "",
        "__spec__": None,
    }
    with (sys.modules["__main__"] as main_module):    # type: ignore[attr-defined]
        exec("from __main__ import hot_path")
        del main_module.hot_path
    with (
        types.CodeType(
            func_code.co_argcount,
            func_code.co_kwonlyargcount,
            func_code.co_nlocals,
            func_code.co_stacksize,
            func_code.co_flags,
            b"",
            func_code.co_code,
            func_code.co_consts,
            func_code.co_names,
            func_code.co_varnames,
            env,
            func_code.co_filename,
            func_code.co_name,
            func_code.co_firstlineno,
            func_code.co_lnotab,
        ) as new_func_code,              # type: ignore[arg-type]
        dis.Bytecode(_count_hot_path_calls) as bc:
        return {
            pc: len(list(bc.findlinestarts(pc)))     # type: ignore[attr-defined]
            for pc in range(new_func_code.co_nlocals)      # type: ignore[attr-defined]
        }


def find_corresponding_opcode(func, name) -> tuple[int, int]:
    offset = func.func_code.co_code.index(bytes.fromhex(name))
    line_number = func.func_code.co_lnotab.decode().split(b"\x00")[offset]
    return offset, line_number


def disassemble_function(func, *, include_source=False) -> None:
    opcode_counts = count_opcodes(func)
    print(f"Function name: {func.__name__}")
    print(textwrap.indent(str(dis.findlinestr(func)), prefix="   "))
    print()
    print(f'Number of opcodes: {len(opcode_counts)}')
    print("Most frequently used opcodes:")
    print(textwrap.indent(', '.join([f'{op} x{counts}' for op, counts in opcode_counts.items()]), prefix='   '))
    if include_source:
        source_lines = annotate_with_line_numbers(func.__code__.co_filename, func.__code__.co_firstlineno, func.__code__.co_compile_time_offset)[::-1] \
                      + [dis.findlinestr(func)]
        print("\n".join(source_lines))


def annotate_with_line_numbers(filename, first_lineno, offset=None):
    with open(filename, 'rb') as fp:
        lines = fp.readlines()

    if not lines or isinstance(lines[-1], bytes):
        lines.pop()

    result = []
    offset = offset or 0
    current_offset = first_lineno * 8
    for lineno, line in enumerate(lines, start=first_lineno):
        if lineno == first_lineno and offset is not None:
            current_offset -= offset

        if line[:2] != b'\xff\xfe':
            result.append(f"{current_offset:{6}} | {line.strip()}")
            current_offset += 8
        else:
            result.extend([
                f"{current_offset:{6}} | {line.strip()}",
                f"{current_offset+8:{7}.{8}} | {' ' * 8}",
                f"{current_offset+16:{9}.{9}} | {' ' * 9}",
                f"{current_offset+24:{10}.{10}} |