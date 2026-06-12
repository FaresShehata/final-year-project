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
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


add5 = curry(add3)(5)                 # (a: int) => b: int => c: int => a+b+c
print(add5(7)(8)(9))


# ── Partial application with `partial` ─────────────────────────────────────────

from functools import partial

add5_10 = partial(add5, 10)
print(add5_10(7))


# ── Trampoline with yield ─────────────────────────────────────────────────────

def increment(x: int) -> int | tuple[int]:
    return x + 1


def inc_trpl(xs: Iterable) -> Iterator[None] | int:
    for x in xs:
        yield from increment(x)
        yield None


xs = [1, 2, 3, 4, 5]
for i in inc_trpl(xs): pass


# ── Itertools ─────────────────────────────────────────────────────────────────

items = ["a", "b", "c"]
for index, item in enumerate(items):
    print(index, item)

for _, item in enumerate(items):
    print(item)

for idx, item in enumerate(range(10)):
    print(idx, item)

print(next(itertools.islice([1, 2, 3], 2)))
print(list(itertools.takewhile(bool, [True, False, True])))
print(tuple(itertools.dropwhile(bool, [True, False, True])))

print(sum(itertools.count()))
print(reversed(range(10)))

it = iter(items)
print(type(it))
next(it)
next(it)
next(it)
try:
    next(it)
except StopIteration as e:
    print(e)

print(sys.getsizeof(items))


# ── Coroutines and send/throw/close ───────────────────────────────────────────

def coroutine() -> Generator[A, A, B]:
    while True:
        value = yield
        print(value)


def run_coroutine(coroutine_fn: Callable[..., Coroutine]) -> None:
    cr = coroutine_fn()
    try:
        next(cr)
        while True:
            value = yield
            cr.send(value)
    except StopIteration as e:
        print(e.value)


coro = coroutine()
run_coroutine(coro)

cr = coroutine()
run_coroutine(coro)

cr = coroutine()
cr.close()


<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|># ── struct — binary packing ───────────────────────────────────────────────────

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

