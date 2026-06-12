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
    """Disassemble function with only annotated opcodes."""
    output = io.StringIO()
    # Use the special `dis` module to get only annotated opcodes.
    dis.dis(fn, file=output)
    return output.getvalue()


def annotate_op(opname):
    """Return a string describing an opcode name and its arguments."""
    try:
        _opnames[opname]
    except KeyError:
        raise ValueError("unknown opcode {!r}".format(opname))
    else:
        return "{:<8s} {}".format(
            opname, ", ".join(_argrepr(argnum, argval) for argnum, argval in _coff.get(opname, []))
        )


def _argrepr(argnum, argval):
    if isinstance(argval, int):
        if argval == 0:
            return f"#{argnum}"
        elif argval is None or argval > 255:
            return "x{}".format(argnum)
        else:
            return "{}".format(argval)
    elif isinstance(argval, bool):
        return ("-" if argval else "+") + "#{}".format(argnum)
    else:
        return "{}={}".format(*_coff.get(opname).get(argnum, ["", ""]))

_cooff = {
    'NOP': [(1, False)],
    'LOAD_CONST': [
        (0, 'const'), (1, 'obj'),
    ],
    'STORE_NAME': [
        (0, 'name')
    ],
    'RETURN_VALUE': [],
}


def demo_bytecode_introspections():
    """Demonstrate byte code introspections."""

    def func(a, b=2, c=None):
        d = a * b / c
        e = [a, b]
        f = {a: b}
        g = {"a": a, "b": b}

        print("d =", d)

        print(e[0], e[-1])
        print(f['c'], f.get('c', None))
        print(g["a"], g.get("a"))

        x = 3
        y = 5
        z = min(x, y)
        w = max(x, y)

        if True:
            continue
        if False:
            break
        while True:
            pass
        while False:
            pass

    print(textwrap.indent(annotated_disassembly(func), "  "))
    print("\n")

    print