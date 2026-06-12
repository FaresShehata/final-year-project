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
    return counts


print(count_opcodes(dis.Bytecode(lambda x: x ** 2)))


# ── Disassembling a module ─────────────────────────────────────────────────────

for name, func in {
    "functools": functools,
}.items():
    print(f"{name}:")
    sdis = annotated_disassembly(func)
    print(textwrap.indent(sdis, prefix="  "))
    print()


# ── Code object lookup ─────────────────────────────────────────────────────────

funcs = [
    (lambda x, y: x * y),
    lambda x, y: x * y,
    (z := lambda z: z**3)(5),
]


for fn in funcs:
    cobj = compile(fn, "<string>", "exec")

    print("\nFunction source:")
    print(cobj.co_code)
    print()

    print("\nFunction bytecode:")
    print(list(dis.get_instructions(cobj)))

    print("\nFunction globals:")
    print(cobj.co_names)


# ── The CPython interpreter's view of the world ────────────────────────────────

c_mainloop = """
int main() { /* ... */ }
""".strip()

if c_mainloop != "":
    try:
        c_obj = compile(c_mainloop, "<mainloop>", mode="exec")

        # Get the C function pointer associated with this code object.
        func_ptr = c_obj.co_code[0]
        print(f"C function pointer: {func_ptr}")
    except Exception as e:
        print(e)


# ── Pyrocks' view of the world ────────────────────────────────────────────────

pyrocks_obj = """
PyObject *PyImport_ExecCodeModule(const char *name, PyCodeObject *co);
"""


# ── Pyrocks is not so smart ───────────────────────────────────────────────────

try:
    co = compile("a = 1", "<stdin>", mode="exec")
    # assert co.co_consts is not None
except AttributeError:
    pass
else:
    raise AssertionError("Should be impossible to get `const`")


# ── Dynamic loading and importing modules ──────────────────────────────────────

module_name = "sys"
spec = importlib.machinery.ModuleSpec(module_name, loader=None)
loader = importlib.abc.Loader(spec)
frozen_module = loader.exec_module(types.ModuleType(module_name))


# ── Hooking module loading ─────────────────────────────────────────────────            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

