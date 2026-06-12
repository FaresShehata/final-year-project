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


# ── Frame inspection ──────────────────────────────────────────────────────────-

def my_frame_info(frame):
    print("Frame info:")
    print(f"{frame.f_code.co_filename}")
    print(f"{frame.f_lineno}")


def get_stack_depth() -> int:
    depth = 0
    frame = sys._getframe(0)
    while frame is not None:
        depth += 1
        frame = frame.f_back
    return depth


def stack_trace(max_frames=5) -> list[tuple[int, str]]:
    frames = []
    for frame in reversed(inspect.trace()):
        frames.append((frame[0], frame[1]))
        if len(frames) >= max_frames:
            break
    return frames[::-1]


# ── Garbage collection ─────────────────────────────────────────────────────────

gc.collect(0)

try:
    gc.garbage.clear()
except AttributeError:
    pass


# ── Traceback and traceback printing ───────────────────────────────────────────

traceback = traceback.format_exc()

print(traceback)


# ── Weak references ────────────────────────────────────────────────────────────

wr = weakref.ref(list(range(10)))

assert wr() is not None     # strong reference
assert wr().values != []    # still live
del wr                     # no longer alive
assert wr() is None         # dead


# ── Slots-based classes ────────────────────────────────────────────────────────

class SlotClass:
    __slots__ = ["x"]

# ── Pickling ──────────────────────────────────────────────────────────────────

pickle_str: bytes = pickle.dumps(SlotClass())
slot_cls: type = pickle.loads(pickle_str)
instance: SlotClass = slot_cls()


# ── Global namespace modification via `sys.modules` ─────────────────────────────

sys.modules[__name__] = SomeNamespace()

for k, v in globals().items():
    setattr(sys.modules[__name__], k, v)


# ── Interlude: try/finally ─────────────────────────────────────────────────────

try:
    raise ValueError("some error")
finally:
    print("finalizing")


# ── Finalization callbacks ─────────────────────────────────────────────────────

@dataclasses.dataclass
class Deleter:
    name: str = dataclasses.field(compare=False)
    value: Optional[int] = properties.maxint

    def __post_init__(self) -> None:
        del self.name       # delete attribute at finalization
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
