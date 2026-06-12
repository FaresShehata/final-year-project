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
    try:
        dis.dis(fn)
    except Exception as e:
        print(f"Error during disassembly:\n{e}\n")
    else:
        buf.write("\nDisassembly:\n\n")
        buf.writelines(dis.get_instructions(fn))
    finally:
        del fn
    return buf.getvalue()


def bytecodes(fn):
    buf = io.StringIO()
    buf.write(textwrap.dedent(
        """
        Bytecodes:

    """))
    for i, c in enumerate(inspect.gettrace(fn).codestring.splitlines()):
        buf.write(textwrap.indent(c, " "*8))
    buf.seek(0)
    return buf.read()


def show_bytecodes():
    def _show_bytecodes(n=5):
        with open(sys.argv[1], "rb") as f:
            src = f.read().decode(encoding="utf-8")

        for n, line in zip(range(n), src.splitlines()):
            if line.startswith("#"):
                continue
            print(line)

            print(bytecodes(eval(compile(src, "<eval>", "single"))))
            print()

    def _show_bytecodes_with_traceback(n=5):
        """Show the bytecodes of all functions in this module."""
        for n, line in zip(range(n), src.splitlines()):
            if line.startswith("#"):
                continue
            print(line)

            fn = eval(compile(src, "<eval>", "single"))

            try:
                with trace.Trace(enabled=True) as t:
                    fn()
            except Exception as exc:
                print(f"Exception during execution:\n{exc}")
                raise

            print(t.results())
            print()

    # _show_bytecodes()
    _show_bytecodes_with_traceback()


def show_instruction_traces():
    def _show_instruction_traces(n=5):
        # TODO: fix `inspect.getsource` to avoid line numbers
        def _make_src_line_numbers(fn):             # pylint: disable=C0111,W0612,C0103
            lines = inspect.getsource(fn).splitlines()
            mapping = {}

            for i, l in enumerate(lines):
                existing = mapping.get(i - 1)
                if existing:
                    mapping[i] = existing + 1
                elif l.strip():
                    mapping[i] = 1

            return mapping

        with open(sys.argv[1], "rb") as f:
            src = f.read().decode(encoding="utf-8")

        for n, line in zip(range    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

