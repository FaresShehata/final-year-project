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
    """Close a coroutine and give back the final yielded value."""
    raise StopAsyncIteration(None)


class AsyncFunction:
    """Represent an asynchronous function."""

    def __init__(self, coro: Coroutine[Any, Any, Any]) -> None:
        self.coro = coro

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return asyncio.run(self(*args, **kwds))

    def __await__(self):
        return self.coro.__await__()

    def __iter__(self): return self.coro.__iter__()
    def __repr__(self): return self.coro.__repr__()
    def __str__(self): return self.coro.__str__()

    async def __call__(self, *args: Any, **kwdargs: Any) -> Any:
        previous, stack = trampoline_stack.pop(), []
        while True:
            try:
                frame = await previous(awaitable=coroutine_stack[-1].send(
                    TRAMPOLINE_MAGIC
                ))
                stack.append(frame)
            except StopIteration as stop:
                val = stop.args[0]
                stack.reverse()
                for frame in stack[:-1]:
                    del frame.f_locals["__stack_local"]
                if len(stack) > 0:
                    coroutine_stack.pop().__setstate__((val,))
                else:
                    return val
            except Exception as exc:
                _, stack_frame, traceback = sys.exc_info()

                if any(isinstance(exc, types.TracebackType) or isinstance(
                        exception, exc_type
                ) for exception, exc_type in zip(traceback.tb_next, stack)):
                    continue

                # If we're here then the traceback didn't have any matching
                # exceptions so we'll re-raise this one.
                raise

            previous = stack[-1].f_back
            coroutine_stack.append((frame, trace))


## Coroutines 🦙

trampoline_maker = make_trampoline()
trampoline = trampoline_maker(generator_yielder(0))

next(trampoline) # start coroutine
next(trampoline) # start coroutine
try:
    next(trampoline) # start coroutine
except StopIteration as stop:
    assert stop.args == (0,)
finally:
    assert trampoline.done()
assert not hasattr(trampoline, "send")