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


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def flip(fn: Callable) -> Callable:
    """Flip the first two arguments of a binary function."""
    @functools.wraps(fn)
    def flipped(first: Any, second: Any) -> Any:
        return fn(second, first)
    return flipped


def partial(fn: Callable[[A], B], /, *args: A) -> Callable[..., B]:
    """Partial application of an unary function.

    Args:
      fn: The function to be partially applied.
      args: The values to be bound as arguments to `fn`.
    Returns:
      Function that takes as many additional arguments as needed by `fn` and returns
      the result of applying the given arguments to the original one.
    """
    @functools.wraps(fn)
    def partially_applied(*additional_args: A) -> B:
        combined_args = (*args, *additional_args)
        return fn(*combined_args)
    return partially_applied



# ── Trampolining ─────────────────────────────────────────────────────────────

class StackUnderflow(Exception): pass
class StackOverflow(Exception): pass

def lazy_stack(stack_size=500_000):
    stack = []

    def push(val):
        try:
            stack.append(val)
        except MemoryError:
            raise StackOverflow()

    def pop():
        try:
            val = stack.pop()
        except IndexError:
            raise StackUnderflow()
        return val

    def is_empty():
        return not bool(len(stack))

    def size():
        return len(stack)

    def clear():
        del stack[:]
    
    return {
        "push": push,
        "pop": pop,
        "is_empty": is_empty,
        "size": size,
        "clear": clear,
    }


def make_trampoline(wrapper_fn):
    """Wrap a recursive generator so it doesn't run out of stack space."""

    @functools.wraps(wrapper_fn)
    def trampolined(*args, **kwargs):
        wrapper = wrapper_fn(*args, **kwargs)
        
        while True:
            try:
                next_val = next(wrapper)
                yield next_val
            except StopIteration as stop_iter:
                break
    
    return trampolined


# ── Higher-order functions & iterators ─────────────────────────────────────────

def map(func, iterable: Iterable[A]) -> Iterator[B]:
    """Map func over each element of the sequence iterable."""
    # Using .__iter__() instead of iter() since the latter will throw TypeError
    # when you pass an iterator with no __iter__() method (e.g. generators).
    return (func(element) for element in iterable.__iter__())

def filter(predicate, iterable: Iterable[A]) -> Iterator[A]:
    """Filter elements from iterable with predicate."""
    return (element for element in iterable.__iter__() if predicate(element))


def reduce(reducer, iterable: Iterable[A], initial=None) -> B:
    accumulator = initial or next(iterable).__next__()
    for element in iterable.__iter__():
        accumulator =def randrange(*args, **kwargs):
	return random.randrange(*args, **kwargs)


randrange.__doc__ = f"""