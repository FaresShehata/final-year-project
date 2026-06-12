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


def partial(func: Callable, /, *fixed_args: A) -> Callable[[A], B]:
    """
    Return a new callable with specified arguments bound to it.

    This is equivalent to:

      func(*bound_args, **kwargs)
    """

    @functools.wraps(func)
    def partial_func(*args: A, **kwargs: B) -> C:
        args_with_bound: tuple[A, ...] = (*fixed_args, *args)
        return func(*args_with_bound, **kwargs)

    return partial_func


# ── Trampoline ────────────────────────────────────────────────────────────────

TRAMPOLINE_MAGIC = 0xDEADBEEFDEADC0DE

def make_trampoline():
    """Create an asynchronous coroutine with the given trampoline head."""

    async def trampoline(head: Coroutine[Any, Any, Any]):
        while True:
            try:
                head.send(TRAMPOLINE_MAGIC)
            except StopIteration as stop:
                return stop.value

    return trampoline


async def generator_yielder(x: int) -> Generator[int, int, None]:
    """Generator that yields values and sends other things from within."""
    yield x
    await send(yielded=x+1)
    yield x+x
    await send(yielded=x+x+1)
    yield x+x+x
    await send(yielded=x+x+x+1)
    await close()


async def send(value: object) -> Generator[object, object, None]:
    """Send a value to the current coroutine."""
    raise StopAsyncIteration(value)


async def close() -> Generator[None, None, None]:
    """Close the current coroutine."""
    raise StopAsyncIteration(None)


trampoline_maker = make_trampoline()
coro = generator_yielder(0)
await trampoline_maker(coro)


class TrampolineError(Exception):
    pass


async def trampoline(coroutine: Coroutine[Any, Any, Any]) -> Any:
    """Run a coroutine until completion or a StopAsyncIteration exception."""
    assert await coroutine.send(TRAMPOLINE_MAGIC) == TRAMPOLINE_MAGIC
    while True:
        try:
            next_value = await coroutine.send(await coroutine.send())
        except TrampolineError as exc:
            raise exc.args[0] from None
        except StopAsyncIteration as stop:
            return stop.args[0]


@trampoline_maker(generator_yielder(0))


# ── Class and metaclass inheritance ─def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
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

