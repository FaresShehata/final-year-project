"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable[A, B]) -> Callable[[A], Callable[[], B]]:
    def inner(arg: A) -> Callable[[], B]:
        return lambda: fn(arg)
    return inner


@functools.lru_cache(maxsize=None)
def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any) -> Any:
        if isinstance(args[-1], dict):         # cache on last arg being dict
            key = tuple(sorted(dict(args[-1]).items()))
            args = (*args[:-1], key)
        elif isinstance(args[-1], set):        # cache on last arg being set
            args = (*args[:-1], frozenset(args[-1]))
        try:
            return cache[args]
        except KeyError as err:
            cache[args] = ret = fn(*args)
            return ret
    return wrapper


# ── Trampoline syntax ─────────────────────────────────────────────────────────

class Trampoline:

    def __init__(self, func: Callable, *args: Any):
        self.func = func
        self.args = args

    def __iter__(self) -> Iterator:
        while True:
            func, args = self.func, self.args
            self.func, self.args = None, None
            yield from func(*args)

@functools.lru_cache()
def trampoline(func: Callable, *args: Any) -> Any:
    return next(Trampoline(func, *args))

# ── Trampolinable function syntax ──────────────────────────────────────────────

trampolineify: Callable[[Callable], Callable] = functools.partial(trampoline, None)


def trampolineify_generator(generator: Generator[Any, None, None]):
    return (next(generator) for i in itertools.count())

@trampolineify_generator
def fib_gen(n: int):
    if n < 2:
        raise StopIteration(n)
    yield from fib_gen(n - 1) + fib_gen(n - 2)

fib: Generator[int, None, None] = trampolineify(fib_gen)


def trampolineify_coroutine(coroutine: Coroutine[Any, Any, Any]):
    return coroutine.send(None)

@trampolineify_coroutine
async def fib_async(n: int):
    if n < 2:
        await asyncio.sleep(0)
        return n
    else:
        left  = fib_async(n-        names.append(frame.f_code.co_name)
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

