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


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    else:
        return Thunk(_odd_tc, n-1, NOT(acc))


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    else:
        return Thunk(_even_tc, n-1, acc)


def even_tramp(n: int) -> bool:
    return _even_tc(n, FALSE)


def odd_tramp(n: int) -> bool:
    return _odd_tc(n, TRUE)


# ── Higher order functions ────────────────────────────────────────────────────

def filter_map(fn: Callable, iterable: Iterable[Any]) -> Iterator:
    for item in iterable:
        if value := fn(item):
            yield value


def map_reduce(fn: Callable, iterable: Iterable[A], reduction: Callable[[A, A], B]):
    return reduce(reduction, map(fn, iterable))


def map_filter(fn: Callable, iterable: Iterable[A], predicate: Callable):
    for item in iterable:
        if predicate(fn(item)):
            yield item


def reduce(fn: Callable, iterable: Iterable[B], initial=None):

    if initial is None:
        it = iter(iterable)
        current = next(it)
    else:
        current = initial
        it = iter(iterable)

    for elem in it:
        current = fn(current, elem)

    return current


def make_compose(fn: Callable, g: Callable) -> Callable:
    return lambda x: fn(g(x))


def make_identity_tuple(x: tuple) -> tuple:
    return x,


identity_tuple = make_identity_tuple


def make_filter(predicate: Callable) -> Callable:
    """
    Turn a single-argument function into a binary function that filters by the first argument.
    """

    def inner(x: int, y: int) -> int:
        return x if predicate(y) else y
    return inner


def make_indexer(length: int) -> Callable:
    """
    Create an indexing function for use with enumerate().
    """
    
    def indexer(i: int) -> int:
        return i % length
    return indexer


def make_splitter(separator: str) -> Callable:
    """
    Turn a string splitter into a generator function that yields the split tokens.

    Note: This version doesn't work with Unicode separators, but works on ASCII.
    """

    def splitter(s: str) -> Iterator[str]:
        last_idx = 0
        for i,        Task(id=i, name=f"Task-{i}") for i in range(7)
    ]
    pending_tasks: list[Tuple[int, Task]] = []

    while True:
        num_pending = len(pending_tasks)
        for idx, task in reversed(sorted(tasks)):
            if task.is_terminal():
                continue
            elif not task.status.is_terminal():
                task.transition(Status.RUNNING)
                task.tags.extend(["in-progress"])
                task.metadata["start"] = time.time()
                try:
                    result = await asyncio.wait_for(
                        task_runner(task), timeout=random.uniform(0.2, 1.9) * 10
                    )
                    print(result)
                except RuntimeError as e:
                    task.transition(Status.FAILED)
                    task.tags.extend(["error"])
                    task.metadata.update({"end": time.time(), "error": e})
                else:
