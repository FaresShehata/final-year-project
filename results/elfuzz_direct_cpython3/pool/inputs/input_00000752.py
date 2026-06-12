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


add2 = compose(add3, lambda a: a - 2)


def partial(func: Callable, /, *bound_args: A, **bound_kwargs: B) -> Callable:
    """Partial application of an arbitrary number of positional and keyword arguments to a callable.

    The returned callable will accept only the remaining positional and keyword arguments.
    """
    argspec = func.__code__.co_varnames
    bound_args_names = set(bound_args)

    def partially_bound_func(*remaining_args, **remaining_kwargs):
        # Handle positional arguments first so that they are applied before keyword arguments
        bound_args_and_remaining_args = list(bound_args)
        bound_args_and_remaining_args.extend(remaining_args)
        missing_posiitional_args = max(len(argspec) - len(bound_args_names),
                                       0) - len(bound_args_and_remaining_args)
        bounded_args = tuple(
            getattr(None, arg_name) for arg_name in argspec[-missing_posiitional_args:]
        ) + tuple(bound_kwargs.get(arg_name) for arg_name in bound_args_names)

        # Combine positional arguments with default values into single sequence
        # This is done to allow us to pass it as a single argument to `func`
        kwargs_with_defaults = {**bound_kwargs, **{arg_name: None for arg_name in argspec}}
        all_args = (*bounded_args, *(kwargs_with_defaults[arg] for arg in argspec))

        return func(*all_args, *remaining_args[missing_posiitional_args:], **remaining_kwargs)

    return partially_bound_func


sum_5 = partial(sum, 5)
sum_7 = partial(sum, 7)


# ── Trampoline recursion (iterative, not tail-recursive) ──────────────────────


class TrampolinedGenerator(Iterator[A]):
    def __init__(self, generator_function: Callable[[Any], Generator]) -> None:
        self._generator = generator_function()
        self._next_yielded_value = next(self._generator)
        self._stack = [self]

    def _step(self) -> bool:
        try:
            while True:
                yield self._next_yielded_value
                self._next_yielded_value = next(self._generator)
        except StopIteration as e:
            del self._stack[:]
            return False

    def __next__(self) -> A:
        if self._stack:
            continue_tramping = self._stack[-1]._step()

            if not continue_tramping:
                raise StopIteration(e.value)
        else:
            continue_tramping = self._step()

        if not continue_tramping:
            raise StopIteration(e.value)
        else:
            return self._next_yielded_value


def bubble_sort(iterable: Iterable[B]) -> Generator[C, None, None]:
    return TrampolinedGenerator(
        lambda: (
            i
            for i in iterable
            if any(i < j for j in itertools.islice(bubble_sort(iterable), i))
        )
    )


if __name__ == "__main__":
    print(church_to_int(int_to_church(sys.argv[1])))