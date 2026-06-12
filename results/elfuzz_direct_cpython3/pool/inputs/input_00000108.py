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

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *rest: curried(*(args + rest))

    return curried


@curry
def add(x: A | B, y: A | B) -> A | B:
    return x + y


# ── Trampoline — efficient tail recursion for infinite streams ────────────────

class Trampoline(Generic[T]):
    """Trampoline: a data structure that represents an operation on a Maybe monad.
       The Maybe monad can be used to represent side-effects or errors without
       changing the core algorithm."""

    __slots__ = ("value", "tail")

    def __init__(self, value: T | Exception | None, tail: Trampoline | None = None):
        self.value = value
        self.tail = tail

    def unwrap(self) -> T:
        if isinstance(self.value, Exception): raise self.value
        elif self.tail is None: return self.value
        else: return self.tail.unwrap()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Trampoline): return NotImplemented

        if self.value == other.value:           # same value?
            if self.tail is None:               # both are done?
                if other.tail is None:          # then both must be done too!
                    return True
                else:                           # but one is done and one isn't?
                    return False

            elif other.tail is None:            # both have tails? they must match!
                return Trampoline.is_done(self.tail) and Trampoline.is_done(other.tail)

            else:                               # both have tails, compare them recursively...
                return self.tail == other.tail
        else:
            return False

    @staticmethod
    def is_done(trampoline: Trampoline | None) -> bool:
        return trampoline is None or trampoline.tail is None

    @classmethod
    def from_exception(cls, exception: Exception) -> Trampoline[Exception]:
        return cls(exception)

    @classmethod
    def from_value(cls, value: T) -> Trampoline[T]:
        return cls(value)

    @classmethod
    def from_tail(cls, tail: Trampoline) -> Trampoline[None]:
        return cls(None, tail)

    @classmethod
    def from_lambda(cls, thunk: Callable[[Trampoline], Trampoline]) -> Trampoline[None]:
        return cls.from_tail(
            Trampoline.from_lambda(lambda _: Trampoline(thunk))

        )


def trampoline(func
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

