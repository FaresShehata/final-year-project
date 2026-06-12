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
        "locals":   frame.f_locals,
        "globals":  frame.f_globals,
        "constants": tuple(map(repr, frame.f_code.co_consts)),
        "filename": frame.f_code.co_filename,
        "lineno":   frame.f_lineno,
        "argcount": frame.f_code.co_argcount,
        "closures": tuple(closure.cell_contents for closure in frame.f_code.co_cellvars),
    }


def call_depth_probes() -> list[tuple[int, dict]]:
    frames: list[tuple[int, dict]] = []
    current_frame = sys._getframe()
    while True:
        try:
            d = caller_info(depth=len(frames))
            frames.append((len(frames), d))
        except ValueError:
            break
        current_frame = current_frame.f_back
    return frames[::-1]


def parsed_call_stack() -> list[inspect.FrameInfo]:
    frames = inspect.stack()[::-1][:-1]      # exclude __main__
    return [inspect.FrameInfo.fromframes(frame) for frame in frames]


# ── Garbage Collection ───────────────────────────────────────────────────────-

gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS | gc.DEBUG_COLLECTABLE |
             gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_OBJECTS |
             gc.DEBUG_SAVEALL | gc.DEBUG_STATS | gc.DEBUG_STATS | gc.DEBUG_TRACE)


# ── Tracing Memory Allocations ────────────────────────────────────────────────

tracemalloc.start(50)
snapshot = tracemalloc.take_snapshot()

for line in annotated_disassembly(hot_path(1_000)).splitlines():
    print(line.strip())
print("")

# ── Weak References ───────────────────────────────────────────────────────────

weak_ref_obj = weakref.ref(hot_path(1_000))

assert hot_path(1_000) is weak_ref_obj()
del hot_path(1_000)
assert weak_ref_obj() is None


# ── Type hinting ──────────────────────────────────────────────────────────────

def add(a: int, b: int) -> int:       # mypy checkable using --check-untyped-defs flag
    return a + b


class Vector2D:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
