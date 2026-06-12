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


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


add2 = add3(2)


# ── Partial application of curried functions ────────────────────────────────

def partial(fn: Callable, /, *args: Any) -> Callable:
    """Partial application of a curried function.

    We can't use functools.partial because it doesn't work with variadic arguments.
    """
    if args and not all(isinstance(arg, type(args[0])) for arg in args[1:]):
        raise TypeError("All arguments must be the same type.")
    elif isinstance(args[-1], Callable):
        return partial(args[-1], *(fn(*args[:-1])))
    else:
        return lambda *more_args: fn(*(args + more_args))


def first_three(xs: list[int]) -> tuple[int]:
    return xs[:3]


first_three_partial = partial(first_three)


# ── Trampoline pattern ─────────────────────────────────────────────────────

class StackUnderflow(Exception):
    pass


class StackOverrun(Exception):
    pass


def eval_tramp(
    stack: list[Any],
    fn: Callable[[list[Any]], tuple[list[Any], bool]],
) -> None:
    while True:
        try:
            head, tail = fn(stack)
            if not tail:
                raise StackUnderflow()
            stack.extend(head)
        except StackOverflow as e:
            raise e.with_traceback(sys.exc_info()[2])


def eval_closures(
    stack: list[Callable]
) -> tuple[list[Callable], bool]:
    while True:
        try:
            func = stack.pop()
            stack.append(func())
        except IndexError:
            break
    return stack, False


def eval_compound(
    stack: list[Any] | list[Callable],
    fn: Callable[[Iterable], Any],
) -> tuple[list[Any] | list[Callable], bool]:
    yield from map(fn, stack[:-1])
    return [stack[-1]], False


def eval_closure(
    stack: list[Callable],
    fn: Callable[[tuple[int]], tuple[tuple[int]]],
) -> tuple[list[Callable], bool]:
    x = stack.pop()
    args = tuple(reversed(fn((x,))))
    return [partial(fn, *args)], False


def eval_subst(
    stack: list[Callable],
    fn: Callable[[Any], Any],
) -> tuple[list[Callable], bool]:
    key, value = stack.pop(), stack.pop()
    stack.extend([lambda d: fn(key(d)), value])
    return [], False


def eval_sum(
    stack: list[Iterable[int]]
) -> tuple[list[int], bool]:
    yield sum(stack)
    return [], False


def eval_product(
    stack: list[Iterable[int]]
) -> tuple[list[int], bool]:
    yield functools.reduce(operator.mul, stack)
    return [], False


def eval_map(
    stack: list[Iterable[Any]]
) -> tuple[list[Any], bool]:
    fn, iterable = stack.pop(), stack.pop()
    yield from map(fn, iterable)
    return [], False


def eval_filter(
    stack: list[Iterable[Any]]
) -> tuple[list[Any], bool]:
    predicate, iterable = stack.pop(), stack.pop()
    yield from filter(predicate, iterable)
    return [], False


def eval_reduce(
    stack: list[Iterable[int]]
) -> tuple[list[int], bool]:
    reducer, initial_value, iterable = stack.pop(), stack.pop(), stack.pop()
    yield functools.reduce(reducer, iterable, initial_value)
    return [], False


def eval_fibonacci(
    stack: list[int]
) -> tuple[list[int], bool]:
    n, prev, curr = stack.pop(), stack.pop(), stack.pop()

    if n == 0 or n == 1:
        stack.extend([prev, curr])
        return [], True

    stack.extend([curr, prev + curr])

    return [], False


def eval_factorial(
    stack: list[int]
) -> tuple[list[int], bool]:
    n, previous_fact = stack.pop(), stack.pop()
    fact = functools.reduce(operator.mul, list(range(previous_fact + 1, n + 1)))
    stack.extend([fact, previous_fact + 1])
    return [], False


def eval_list(
    stack: list[int]
) -> tuple[list[int], bool]:
    n, lst = stack.pop(), stack.pop()
    if n > 0:
        stack.extend    ([lambda x: x - 1], lambda x: x - 1),
    ([lambda _, y: y + 1], lambda x: lambda y: y + 1),
    ([lambda x, y: x + y], lambda x: lambda y: x + y),
    ([], lambda x: []),
    ([lambda