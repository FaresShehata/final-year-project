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
    if not callable(arity):
        raise ValueError(
            "Invalid number of arguments passed to `curry`. "
            "The wrapped argument has an invalid value.",
        )
    
    def wrapper(*args: A):
        if len(args) == arity:
            return fn(*args)
        
        def inner(*inner_args: A):
            return wrapper(*(list(args) + list(inner_args)))
        
        return inner
    
    return wrapper

@functools.lru_cache(maxsize=None)
def memoize(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @functools.wraps(func)
    def wrapper(*arg: Any):
        if arg in wrapper.cache:
            return wrapper.cache[arg]
        else:
            result = func(arg)
            wrapper.cache[arg] = result
            return result
    
    wrapper.cache = {}
    return wrapper


# ── Partial application and composition with lambdas ────────────────────────

def compose_with_lambda(composition_list: list[Callable]):
    return (
        lambda *args: reduce(operator.compose, composition_list)(*args)
    )


# ── Trampoline functions ───────────────────────────────────────────────────

def trampoline(f: Callable[[Any], Generator[Any, None, Any]]) -> Any:
    """Run the generator as many times as needed to return a value."""
    while True:
        try:
            result = next(f())
        except StopIteration as e:
            return e.value

def _summands_generator(numbers: Iterable[int]) -> Generator[int, None, int]:
    """Calculate the summands from a range of numbers."""
    total = 0
    for number in numbers:
        yield number
        total += number
    return total

def is_even(number: int) -> bool:
    return number % 2 == 0

def is_odd(number: int) -> bool:
    return number % 2 != 0

def even_or_odd_trampoline(numbers: Iterable[int]) -> bool:
    """Check if any number in a sequence is odd using a trampoline."""
    generator = _summands_generator(numbers)
    return trampoline((lambda: (yield from generator))()) or False


if __name__ == "__main__":
    # ── Lambda-calculus church encodings ─────────────────────────────────────
    print(church_to_int(int_to_church(4)))