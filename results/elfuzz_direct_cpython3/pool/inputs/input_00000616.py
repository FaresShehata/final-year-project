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
    """Accumulate and average a sequence of numbers."""

    total = init
    count = 0

    def accumulate(value: float) -> float:
        nonlocal total, count
        total = total + value
        count = count + 1
        return total / count

    return accumulate


# ── Partial application with variables as parameters ───────────────────────────

def take_n(func: Callable, n: int) -> Callable[[Iterable[A]], list[B]]:
    """Generate the first N results from a unary function over iterables."""
    return lambda iterable: list(itertools.islice(map(func, iterable), n))


def is_odd_count(items: Iterable[int]) -> bool:
    return sum(map(bool, filter(operator.not_, items))) % 2 != 0


def match_pattern(pattern: str, string: str) -> bool:
    """Match against a pattern using regular expression syntax.

    >>> match_pattern(r"\w+@\w+\.\w+", "alice@example.com")
    True
    """
    return re.match(pattern, string) is not None


def identity(value: A) -> A:
    return value


def get_last_item(item_list: list[A]) -> A | None:
    return item_list[-1]


def map_with_index(items: Iterable[A]) -> Iterator[tuple[int, B]] | None:
    index = 0
    try:
        for item in items:
            yield index, item
            index += 1
    except StopIteration:
        pass


def reduce_by_key(
    items: Iterable[tuple[Any, B]],
    key: Callable[[tuple[Any, B]], Any],
    initial_reduce: Callable[[Any, B], B],
    merge_reducer: Callable[[B, B], B] = operator.add,
) -> dict[Any, B]:
    groups: dict[Any, list[B]] = {}
    for k, v in items:
        g = groups.setdefault(key((k, v)), [])
        g.append(v)
    reduced_groups = {
        k: reduce(initial_reduce, values, initial_value or [])
        for k, values in groups.items()
    }
    return {k: merge_reducers(k, vs) for k, vs in reduced_groups.items()}


def unmap_and_sum(iterable: Iterable[tuple[T, int]]) -> T | None:
    return next((item for item, count in iterable if count == 1), None)


# ── Trampoline algorithm for tail-recursive factorial computation ────────────

FACTORIAL_CACHE = {}


def factorial(n: int) -> int:
    """Compute the factorial of an integer using a recursive algorithm.
    
    Intended to be used only on small inputs where stack overflow is unlikely.
    For larger inputs, it's likely that the stack will overflow before reaching
    the base case.
    """

    # Check cache lookup
    if n == 0:
        return FACTORIAL_CACHE.get(0, 1)
    elif n < 0:
        raise ValueError("Factorial is undefined for negative numbers.")

    # Compute recursively
    if n <= 2:
        return 1

    # Either cache the computed value or call itself
    return (
        FACTORIAL_CACHE.get(n,            raise ValueError("Unknown protocol")


# ─── Walrus Operator ─────────────────────────────────────────────────────────

async def wait_for_seconds(seconds: int) -> None:
    await asyncio.sleep(seconds)


async def main() -> None:
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        print(f"Current elapsed time: {elapsed:.2f}s")
        if elapsed > 3.0:
            break
        await wait_for_seconds(random.randint(1, 4))


asyncio.run(main())


# ─── Typing Generics ─────────────────────────────────────────────────────────

def count_duplicates(items: Iterable[_T]) -> tuple[int, Counter[_T]]:
    counter: Counter[_T] = Counter()
    for item in items:
        counter[item] += 1
    duplicates_count = sum(count for _, count in counter.items()) - len(counter.keys())
    return duplicates_count, counter


# ─── Exception Groups ─────────────────────────────────────────────────────