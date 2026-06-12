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

def flatten(opcount, opcodes) -> tuple[list[tuple[str, int]], ...]:
    acc: list[tuple[str, int]] = []
    for i in range(opcount):
        opcode = opcodes[i]
        if opcode.opname.startswith(("LOAD_GLOBAL", "LOAD_ATTR")) and len(acc) > 0:
            yield tuple(reversed(acc)) + ((opcode.opname, opcode.arg),)
            acc.clear()
        else:
            acc.append((opcode.opname, opcode.arg))


for fncodes in (
    annotated_disassembly(lambda x: x.upper()),
    annotated_disassembly(lambda x: x.lower()),
):
    for opcodes in flatten(*list(map(count_opcodes, map(dis.Bytecode, filter(None, re.findall(r"(?<=^).+", fncodes)))))):
        print(opcodes)


# ── Disassembling an arbitrary function’s bytecode ─────────────────────────────

def annotate_function(fn, *, indent=True) -> str:
    buf = io.StringIO()
    dis.disassemble(fn, file=buf)
    output = buf.getvalue().rstrip()
    buf.close()

    lines: list[str] = []
    current_indentation = ""

    for line in output.splitlines():
        if not line or line.strip() == ">>>":
            continue
        indentation = line.split()[0].lstrip()

        if indent and indentation != current_indentation:
            lines.append(indent.rstrip() + "\n" + line.lstrip())

        elif indentation < current_indentation:
            while indentation < current_indentation:
                lines[-1] = lines[-1][len(current_indentation):]
                current_indentation = ""
            lines.append(line.lstrip())

        else:
            lines.append(line.lstrip())
            current_indentation = indentation

    return "\n".join(lines)


fn = lambda x: x.upper()
print(annotate_function(fn))


# ── The CPython type hierarchy ───────────────────────────────────────────────────

def walk_types(types) -> str:
    result = ["\n"]
    for t in types:
        result.extend([
            f"class {t.__module__}.{t.__qualname__}({t.__bases__[0].__qualname__}) {{",
            "    pass"
        ])
        if hasattr(t, "__mro__"):
            result.append(walk_types(t.__mro__))
        if hasattr(t, "__subclasses__"):
            result.append(walk_types(t.__subclasses__()))
       
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
    print(inspect.getmembers(cobj.globals))


# ── Reading the byte code of a function definition ─────────────────────────────

cobj = compile(lambda x, y: x*y, "<source>", "eval")


def read_bytecode(obj: types.CodeType) -> bytes:
    with open("<bytecode-file>", "wb") as fp:
        fp.write(struct.pack("<HHH", obj.co_argcount, obj.co_stacksize, obj.co_flags))
        fp.write(b"\x00\x00\x00\x00")
        fp.write(struct.pack("<I", id(obj)))
        fp.write(obj.co_consts)
        fp.write(obj.co_names)
        fp.write(obj.co_varnames)
        fp.write(obj.co_filename.encode())
        fp.write(b"\x00" * 6)
        fp.write(obj.co_lnotab[1:])
        fp.seek(8, io.SEEK_CUR)
        fp.write(struct.pack("<{}B".format(len(obj.co_code)), *obj.co_code))
        fp.write(b"\xff\xff\xff\xff")


read_bytecode(cobj)


# ── Structs & arrays ───────────────────────────────────────────────────────────

a: array.array[int] = array.array("i", [1, 2])
b: array.array[float] = array.array("f", [1.0, 2.0])

print(a.tobytes()[:20], b.tobytes()[:20])


class Struct(ctypes.Structure):
    _fields_ = [("value", ctypes.c_uint16)]


struct_a = Struct(value=0xdeadbeef)
struct_b = Struct.from_buffer_copy(bytes([0xde, 0xad, 0xbe, 0xef]))

print(bytes(struct_a))

bytes_struct_a = struct_a.to_bytes(length=len(struct_a), byteorder=sys.byteorder)
print(bytes_struct_a)

if bytes_struct_a == struct_b:
    assert True


# ── Memoryviews & buffers ───────────────────────────────────────────────────────

print(array.array("u", ["αβγδ"]).tofile(filepath=None))

memview = memoryview(b"föö")

print(memview.tolist())


# ── Pickling & unpickling ───────────────────────────────────────────────────────

pickled = pickle.dumps(["a", "b", "c"])

unpickled = pickle.loads(pickled)

print(unpickled)


# ── Copyreg# ── Hooking module loading ─────────────────────────────────────────────────            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

