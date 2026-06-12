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
        if instr.opname.startswith("LOAD"):
            opcode = instr.opname[5:]
        else:
            opcode = instr.opname.lower()

        counts[opcode] = counts.get(opcode, 0) + 1
    return counts


def annotate_opcode_counts(fn) -> str:
    counts = count_opcodes(fn)

    def op(name: str, offset: int) -> str:
        return f"{name:<8}: {counts[name]:>4} @ {offset}"

    buf = io.StringIO()
    for offset, instr in enumerate(dis.get_instructions(fn)):
        print(op(instr.opname, offset), end=" ", file=buf)
    return buf.getvalue()


def get_function_code(fn) -> types.CodeType:
    """Get the compiled code object for a function or method."""
    return fn.__code__

# ── Disassembler API ──────────────────────────────────────────────────────────


def disasm(obj, *, show_source=False) -> str:
    """Disassemble an object's code, with source and bytecodes included."""
    if hasattr(obj, "__code__"):       # Callable?
        code = obj.__code__
    elif isinstance(obj, (types.CodeType, types.FunctionType)):  # CodeObject?
        code = obj.type(code)
    else:                               # Unknown type.
        raise ValueError(f"object is not callable ({type(obj)})")

    name = getattr(obj, "__name__", "<lambda>")
    source = getattr(getattr(obj, "__closure__", None).__getitem__(0),
                     "co_filename",
                     "<sourceless lambda>")
    buf = io.StringIO()
    try:
        dis.dis(
            code,
            file=buf,
            show_offsets=True,
            label_prefix=name,
            label_suffix=f"@ {source}",
            label_file=sys.stdout,
            line_prefix=None,
            max_line_length=None,
            omit_lineno=False,
            omit_frame_header=False,
            omit_frame_footer=False,
            omit_stack_depth=False,
            omit_return_address=False,
            omit_locals=False,
            omit_reversed_ops=False,
            omit_invalid_operands=False,
            omit_unknown_operands=False,
            omit_unused_labels=False,
            omit_unused_codes=False,
            omit_unused_names=False,
            omit_unused_constants=False,
            omit_unused_excnames=False,
            omit_unused_argnames=False,
            omit_unused_subscopes=False,
            omit_unused_closure_vars=False,
            omit_unused_freevars=False,
            omit_unused_cellvars=False,
            omit_unused_globals=False,
            omit_unused_locals=False,
            omit_unused_decorators=False,
            omit_unused_annotations=False,
            omit_unused_keywords=False,
            omit_unused_arguments=False,
            omit_unused_defaults=False,
            omit_unused_varargs=False,
            omit_unused_kwargs=False,
            omit_unused_rest_args=False,
            omit_unused_starred_args=False,
            omit_unused_unpacking_targets=False,
            omit_unused_unpacking_sources=False,
            omit_unused_unpacking_patterns=False,
            omit_unused_unpacking_sequences=False,
            omit_unused_unpacking_lists=False,
            omit_unused_unpacking_tuples=False,
            omit_unused_unpacking_sets=False,
            omit_unused_unpacking_dictionaries=False,
            omit_unused_unpacking_frozensets=False,
            omit_unused_unpacking_dicts=False,
            omit_unused_unpacking_sequents=False,
            omit_unused_unpacking_tuples_and_sets=False,
            omit_unused_unpacking_tuples_and_sequents=False,
            omit_unused_unpacking_tuples_and_sets_and_dicts=False,
            omit_unused_unpacking_tuples_and_sequents_and_dicts=False,
            omit_unused_unpacking_tuples_and_sequents_and_dicts_and_frozensets=False,
            omit_unused_unpacking_tuples_and_sequents_and_dicts_and_frozensets_and_dicts=False,
            omit_unused_unpacking_tuples_and_sequents_and_dicts_and_f    S_ISGID    = 0o2000
    S_ISVTX    = 0o1000
    S_IMMUTABLE= 0o4000
    S_APPEND    = 0o2000
    S_DSYNC     = 0o1000
    S_ODSYNC    = 0o0400
    S_NOATIME   = 0o0200
    S_NODIRATIME= 0o0100
    S_RELATIME  = 0o0040
    S_SYNC      = 0o0020
    S_DIRSYNC   = 0o0010
    S_CHMOD     = 0o0330
    S_CHOWN     = 0o0666
    S_CHGRP     = 0o0220
    S_CLOEXEC   = 0o0001
    S_CREAT     = 0o0002
    S_EXCL      = 0o0004
    S_TRUNC     = 0o0008
    S_APPEND    = 0o0010
    S_NONBLOCK  =