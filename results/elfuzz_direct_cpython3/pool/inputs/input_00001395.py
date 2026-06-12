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


def get_instructions(fn) -> dict:
    base_instr = "<unknown>"
    counts = count_opcodes(fn)

    def _get_instr(instr):
        if base_instr == "<unknown>" and instr.base is not None:
            base_instr = instr.base.opname
        return instr.offset, f'{instr.opname}({",".join(map(str, instr.argvals))})'

    return sorted([(v, _get_instr(instr)) for k, v in counts.items()])


def get_source(fn) -> str:
    with open(inspect.getsourcefile(fn)) as fp:
        return fp.read()


def get_docstring(fn) -> str | None:
    return fn.__doc__ or ""


def compile_fn(fn, filename="<fn>", flags=None) -> types.CodeType:
    assert isinstance(fn, types.FunctionType)
    return compile(get_source(fn), filename, "exec", flags or "exec")


def build_frame(f_globals: dict[str, Any], f_locals: dict[str, Any]) -> types.FrameType:
    return types.FrameType(
        globals=f_globals,
        locals=f_locals,
        f_back=sys._getframe(),
        f_trace=None,
        f_code=get_code_obj(type(f_globals)),
    )
    

# ───────────────────────────────────────────────────────────────────────────────

obj = {
    "__annotations__": {
        "_a_def_": int,
        "_b_def_": float,
        "_c_def_": str,
    },
}


class MyClass:
    """MyClass docstring."""

    a_def_: int = 42
    b_def_: float = 3.14e-56
    c_def_: str = "Hello, world!"
    
    def __init__(self):
        self.a_inst_: int = 42
        self.b_inst_: float = 3.14e-56
        self.c_inst_: str = "Hello, world!"
    
    def method(self):
        pass
    
obj["m"] = MyClass()


# ── Disassemble & bytecode analysis ────────────────────────────────────────────

obj["dis"] = (
    annotated_disassembly(obj["m"].method),
    count_opcodes(obj["m"].method),
    get_instructions(obj["m"].method),
)


# ── Code Objects ───────────────────────────────────────────────────────────────

# Get the actual code object
code = obj["m"].method.__code__

print(code.co_name)
print(code.co_filename)
print(code.co_firstlineno)
print(code.co_consts)


# Find out what's inside of it.

for i in range(len(code.co_varnames)):
    print((i, code.co_names[i], code.co_cellvars[i]))


# ───────────────────────────────────────────────────────────────────────────────

MAGIC_NUMBER: int = marshal.dumps(b"bz2").hex()

foo = [ctypes.c_char_p(MAGIC_NUMBER.encode())]
assert foo[0].value.hex().zfill(8) == MAGIC_NUMBER

bar = array.array("I")
bar.frombytes(foo[0].value)
assert bar.tobytes().hex().zfill(8 * len(bar)) == MAGIC_NUMBER

baz = struct.Struct("<Q").pack_int64(ctypes.addressof(foo[0]))
assert baz.hex()[:8] == MAGIC_NUMBER


# ── Pickling ──────────────────────────────────────────────────────────────────

pickle_string = pickle.dumps(MyClass).decode()


# ── Copying ───────────────────────────────────────────────────────────────────

copy_reg = marshal.loads(pickle_string.encode())


# ── Import