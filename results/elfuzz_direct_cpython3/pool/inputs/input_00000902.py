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


add3 = add3.currier() # same as `add3` but auto-curried when called with fewer than three arguments

add4 = curry(int.__add__)


# ── Partial application ─────────────────────────────────────────────────────

def partial(func: Callable[[A], B], /, *args: A) -> Callable[..., B]:
    """Returns a partially-applied function of the given func."""
    
    @functools.wraps(func)
    def wrapper(*psb_args: B):
        args = (*args, *psb_args)
        return func(*args)

    return wrapper



# ── Trampolining ───────────────────────────────────────────────────────────

class TrampolineError(Exception): pass

def trampoline_aware_caller(callable_, /, *args):
    try:
        result = callable_(*args)
    except ValueError:
        raise TrampolineError from None
    while isinstance(result, Callable):
        try:
            result = result()
        except TrampolineError:
            break
    else:
        return result

trampoline_aware_call = functools.partial(trampoline_aware_caller)


def trampoline(coro: Coroutine[Any, Any, T]) -> T:
    """Trampoline implementation."""

    async def wrapper():
        while True:
            try:
                yield await coro.__anext__()
            except StopAsyncIteration as e:
                return e.value
    
    return trampoline_aware_call(wrapper().__aiter__(), __await__)