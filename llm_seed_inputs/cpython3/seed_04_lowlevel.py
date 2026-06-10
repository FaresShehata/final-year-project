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
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
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

    # memoryview slicing without copy
    mv_a = memoryview(a)
    mv_b = memoryview(b)

    # element-wise product into a new array
    c = array.array("d", (mv_a[i] * mv_b[i] for i in range(len(a))))

    # cast to bytes and back
    raw = bytes(a)
    restored = array.array("d")
    restored.frombytes(raw)

    # frombuffer from struct pack
    buf = struct.pack("5i", 10, 20, 30, 40, 50)
    int_arr = array.array("i")
    int_arr.frombytes(buf)

    return {
        "a":        list(a),
        "b":        list(b),
        "a_dot_b":  list(c),
        "restored": list(restored),
        "int_arr":  list(int_arr),
        "mv_slice": list(mv_a[2:5].tolist()),
    }


# ── ctypes ────────────────────────────────────────────────────────────────────

class CPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    def __repr__(self) -> str:
        return f"CPoint({self.x}, {self.y})"


class CRect(ctypes.Structure):
    _fields_ = [("origin", CPoint), ("width", ctypes.c_double), ("height", ctypes.c_double)]

    def area(self) -> float:
        return self.width * self.height


def ctypes_ops() -> dict:
    pts = (CPoint * 4)(
        CPoint(0.0, 0.0),
        CPoint(1.0, 0.0),
        CPoint(1.0, 1.0),
        CPoint(0.0, 1.0),
    )

    rect = CRect(origin=CPoint(2.0, 3.0), width=4.5, height=2.0)

    # access raw bytes
    raw = bytes(rect)

    # create a ctypes int array and mutate
    arr = (ctypes.c_int * 5)(1, 2, 3, 4, 5)
    for i in range(len(arr)):
        arr[i] *= arr[i]

    # pointer arithmetic
    p_int = ctypes.pointer(ctypes.c_int(42))
    p_int.contents.value += 1

    return {
        "points":     [repr(pts[i]) for i in range(4)],
        "rect_area":  rect.area(),
        "rect_bytes": len(raw),
        "int_arr_sq": list(arr),
        "ptr_val":    p_int.contents.value,
    }


# ── pickle & copyreg ─────────────────────────────────────────────────────────

class Colour:
    __slots__ = ("r", "g", "b")

    def __init__(self, r: int, g: int, b: int):
        self.r, self.g, self.b = r, g, b

    def __repr__(self) -> str:
        return f"Colour({self.r},{self.g},{self.b})"

    def __reduce__(self):
        return (Colour, (self.r, self.g, self.b))


def _colour_reducer(c: Colour):
    return Colour, (c.r, c.g, c.b)


import copyreg
copyreg.pickle(Colour, _colour_reducer)


def pickle_roundtrip(obj: Any, protocol: int = pickle.HIGHEST_PROTOCOL) -> tuple[Any, bytes]:
    raw = pickle.dumps(obj, protocol=protocol)
    return pickle.loads(raw), raw


def pickletools_analysis(obj: Any) -> str:
    raw = pickle.dumps(obj)
    buf = io.StringIO()
    pickletools.dis(raw, out=buf)
    return buf.getvalue()


# ── marshal ───────────────────────────────────────────────────────────────────

def marshal_code_object(fn) -> tuple[bytes, types.CodeType]:
    raw = marshal.dumps(fn.__code__)
    restored: types.CodeType = marshal.loads(raw)  # type: ignore[assignment]
    return raw, restored


# ── importlib — synthetic module ─────────────────────────────────────────────

def create_synthetic_module(name: str, source: str) -> types.ModuleType:
    spec = importlib.util.spec_from_loader(name, loader=None)
    module = types.ModuleType(name)
    module.__spec__ = spec  # type: ignore[assignment]
    exec(compile(source, f"<{name}>", "exec"), module.__dict__)
    sys.modules[name] = module
    return module


# ── gc & weakref ─────────────────────────────────────────────────────────────

class Mortal:
    _alive: int = 0

    def __init__(self, label: str):
        self.label = label
        Mortal._alive += 1

    def __del__(self):
        Mortal._alive -= 1


def gc_demo() -> dict:
    # create a reference cycle
    a: dict = {}
    b: dict = {"partner": a}
    a["partner"] = b
    refs_before = Mortal._alive

    m1 = Mortal("m1")
    m2 = Mortal("m2")
    ref_m1 = weakref.ref(m1)

    alive_with = Mortal._alive
    del m1
    gc.collect()
    alive_after_m1 = Mortal._alive
    ref_valid = ref_m1() is not None  # m1 is gone, but m2 still alive

    del m2
    gc.collect()

    del a, b
    collected = gc.collect()

    return {
        "alive_with_two":    alive_with,
        "alive_after_del_m1": alive_after_m1,
        "weakref_valid":     ref_valid,
        "cycle_collected":   collected >= 0,
    }


# ── tracemalloc ───────────────────────────────────────────────────────────────

def tracemalloc_snapshot() -> dict:
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    # allocate some objects
    big_list = [bytearray(1024) for _ in range(50)]

    snapshot_after = tracemalloc.take_snapshot()
    top_stats = snapshot_after.compare_to(snapshot_before, "lineno")

    tracemalloc.stop()
    del big_list

    return {
        "n_diffs": len(top_stats),
        "top_file": top_stats[0].traceback[0].filename if top_stats else None,
    }


# ── inspect module ────────────────────────────────────────────────────────────

def inspect_demo(fn) -> dict:
    sig = inspect.signature(fn)
    src = inspect.getsource(fn) if inspect.isfunction(fn) else None
    return {
        "name":        fn.__name__,
        "params":      list(sig.parameters.keys()),
        "annotations": {k: str(v.annotation) for k, v in sig.parameters.items()},
        "is_coroutine": inspect.iscoroutinefunction(fn),
        "qualname":    fn.__qualname__,
        "source_len":  len(src) if src else 0,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=== Bytecode analysis ===")
    opcodes = count_opcodes(hot_path)
    print(f"  hot_path opcodes: {opcodes}")
    print(annotated_disassembly(hot_path)[:800])

    print("\n=== Code object surgery ===")
    renamed = clone_with_name(hot_path, "cooler_path")
    print(f"  original name: {hot_path.__name__!r}, cloned: {renamed.__name__!r}")
    add7 = make_adder_from_bytecode(7)
    print(f"  add7(10)={add7(10)}, add7(100)={add7(100)}")

    print("\n=== Frame inspection ===")
    def outer():
        def inner():
            return caller_info(depth=0)
        return inner()
    info = outer()
    print(f"  caller function: {info['function']!r}, line: {info['line']}")
    print(f"  call stack: {depth_probe()[:6]}")

    print("\n=== struct / binary packing ===")
    header = pack_header(0xDEADBEEF, 1, 4, b"PYTH")
    parsed = unpack_header(header)
    print(f"  header bytes: {header.hex()}")
    print(f"  parsed: {parsed}")
    pts = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0)]
    buf = interleave_struct(pts)
    print(f"  interleaved {len(pts)} points -> {len(buf)} bytes")

    print("\n=== array & memoryview ===")
    ao = array_ops()
    for k, v in ao.items():
        print(f"  {k}: {v}")

    print("\n=== ctypes ===")
    co = ctypes_ops()
    for k, v in co.items():
        print(f"  {k}: {v}")

    print("\n=== pickle roundtrip ===")
    original = [Colour(255, 0, 0), Colour(0, 255, 0), Colour(0, 0, 255)]
    restored, raw = pickle_roundtrip(original)
    print(f"  raw size: {len(raw)} bytes")
    print(f"  restored: {restored}")

    print("\n=== pickletools (excerpt) ===")
    analysis = pickletools_analysis({"key": [1, 2, 3]})
    print(textwrap.indent(analysis[:300], "  "))

    print("\n=== marshal code object ===")
    raw_co, restored_co = marshal_code_object(hot_path)
    print(f"  marshalled {len(raw_co)} bytes, restored co_name={restored_co.co_name!r}")

    print("\n=== synthetic importlib module ===")
    mod = create_synthetic_module(
        "_seed04_synth",
        "def hello(name): return f'Hello, {name}!'\nVERSION = (0, 1, 0)",
    )
    print(f"  mod.hello('world') = {mod.hello('world')}")  # type: ignore[attr-defined]
    print(f"  mod.VERSION = {mod.VERSION}")                # type: ignore[attr-defined]

    print("\n=== gc & weakref ===")
    gc_res = gc_demo()
    for k, v in gc_res.items():
        print(f"  {k}: {v}")

    print("\n=== tracemalloc ===")
    tm = tracemalloc_snapshot()
    print(f"  snapshot diff entries: {tm['n_diffs']}")

    print("\n=== inspect ===")
    info2 = inspect_demo(hot_path)
    for k, v in info2.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
