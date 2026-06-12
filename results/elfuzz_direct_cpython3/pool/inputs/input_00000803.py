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


# ── Trampoline functions ─────────────────────────────────────────────────────

def run_trampolined_function(func: Callable[..., Any], /, *args, **kwargs) -> Any:
    """Run a trampolined function until it returns a non-generator or doesn't need to be called again.

    If the function yields a generator, continue calling it until no more results are needed.
    """
    while True:
        result = func(*args, **kwargs)
        if not isinstance(result, Generator):
            return result
        else:
            gen_result = next(result)
            if gen_result == CONTINUE:
                continue
            elif gen_result == HALT:
                break



CONTINUE = object()
HALT = object()

def trampoline(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap a given function such that it can be used as a trampoline."""

    @functools.wraps(func)
    def trampolined(*args, **kwargs):

        def call_with_halt(e):
            return HALT, e

        def call_with_continue(e):
            return CONTINUE, e

        result = func(*args, **kwargs)
        while True:
            try:
                result = call_with_continue(result)
            except RecursionError:
                raise RuntimeError('Function resulted in infinite recursion')
            else:
                if result is CONTINUE:
                    result = yield from result
                elif result is HALT:
                    return result
                else:
                    return result


    return trampolined


# ── Higher-order functions & functional programming tools ─────────────────────

map_ = map
filter_ = filter
reduce_ = reduce
zip_ = zip
enumerate_ = enumerate

def compose_right(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Composes a series of functions together in reverse order using `compose`.

    >>> def inc(x): return x + 1
    >>> def mul2(x): return x * 2
    >>> def inc_mul2(x): return inc(mul2(x))
    >>> print(compose_right(inc, mul2)(5))
    12
    >>> print(compose_right(inc, mul2)(6))
    14
    """

    def _composed(*args, **kwds):
        return compose(*reversed(functions))(*args, **kwds)

    return _composed


def compose_left(*functions
import functools
from typing import Any, Callable, Union

# ── Composition & Applicative order evaluation ─────────────────────────────────

