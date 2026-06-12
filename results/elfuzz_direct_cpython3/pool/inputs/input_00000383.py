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
def add(a: A, b: B) -> C:
    return a + b



# ── Partial application & currying with lambdas ───────────────────────────────

add_2 = add(2)

add_2_lambda = lambda b: add(b, 2)


# ── Trampoline- and tail recursion using decorators ───────────────────────────

def trampoline(func):
    """Decorate a generator-based coroutine to use the trampoline pattern."""

    @wraps(func)
    def wrapper(*args, **kwargs):

        # The trampoline is just a stack of yielded values.
        # We can traverse it using the `yield from` syntax.
        result = func(*args, **kwargs)
        while True:
            try:
                yield next(result)
            except StopIteration as stop:
                break

    return wrapper

@trampoline
def countdown(count: int) -> Iterator[int]:
    if count > 0:
        yield from countdown(count - 1)
        yield count
    else:
        yield None


# ── Comprehensions, generators & iterators ───────────────────────────────────-

def first(iterable: Iterable[A]) -> A | None:
    iterator = iter(iterable[::-1])
    try:
        return next(iterator)
    except StopIteration:
        return None


def get_last(iterable: Iterable[A]) -> A | None:
    iterator = iter(iterable[::-1])
    last_val = next(iterator)
    for val in iterator:
        last_val = val
    return last_val


def flatten(iterables: Iterable[Iterable[A]]) -> Iterator[A]:
    for iterable in iterables:
        for item in iterable:
            yield item

def cartesian_product(a: Iterable[Any], b: Iterable[Any]) -> Iterator[tuple[A, B]]:
    for x in a:
        for y in b:
            yield x, y


# ── Generators & iterators basics ─────────────────────────────────────────────

def fibs() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def all_fibs_less_than(max_value: int) -> Iterator[int]:
    for fib in fibs():
        if fib < max_value:
            yield fib
        else:
            return


def permutations(sequence: Iterable[A]) -> Iterator[list[A]]:
    if not sequence:
        yield []
    for index, element in enumerate(sequence):
        rest_elements = list(sequence[:index] + sequence[index+1:])
        for permutation_of_rest in permutations(rest_elements):
            yield [element] + permutation_of_rest

def prime_factors(n: int) -> Iterator[int]:
    i = 2
    while i*i <= n:
        if n % i == 0:
            n //= i
            yield i
        else:
            i += 1
    if n != 1:
        yield n


# ── Generators, iterators & coroutines ────────────────────────────────────────

def fibonacci() -> Generator[int, None, None]:
    yield 0
    current, new = 0, 1
    while True:
        current, new = new, current + new
        yield current


def countdown_coroutine(count: int) -> Iterator[int]:
    while count > 0:
        yield count
        count -= 1


def countdown_coroutine_with_yield_from(count: int) -> Iterator[int]:
    while count > 0:
        yield from countdown_coroutine_with_yield_from(count - 1)
        yield count


def countdown_coroutine_with_send() -> Iterator[int]:
    while True:
        value = yield
        print(value)
        if hasattr(value, "stop"):  # Check whether we're done.
            break
        yield value - 1


def countdown_coroutine_with_throw() -> Iterator[int]:
    while True:
        try:
            value = yield
            print(value)
        except ZeroDivisionError:
            continue


def countdown_coroutine_with_close() -> Iterator[int]:
    try:
        while True:
            value = yield
            print(value)
    finally
class AbstractClassABC(abc.ABC):

    """Abstract class using ABCMeta which has no methods of its own."""

    pass


@RegistryMeta.register
class ConcreteDerived(AbstractClassABC):

    """Concrete subclass of an abstract base class."""

    pass


@RegistryMeta.register
class AnotherConcreteDerived(AbstractClassABC):

    """Another concrete subclass of an abstract base class."""

    pass


# ── Class decorator example ───────────────────────────────────────────────────

def debug_all(func: Callable[..., T], *, prefix="debug_"):
    """
    Decorate functions by adding debugging statements around them.

    Args:
      prefix (str): Prefix for the generated debugging statement(s).
    """

    def wrapper(*args, **kwds) -> T:
        print(f"{prefix}{func.__name__}: entering")
        try:
            result = func(*args, **kwds)
            print(f"{prefix}{func.__name__}: exiting returning {result!r}")
            return result
        except Exception as e:
            print(f"{prefix}{func.__name__}: exiting raising {e!r}", file=sys.stderr)
            raise
    return wrapper


# ── Type hinting examples ─────────────────────────────────────────────────────

def foo(a: Foo) -> bool:
    ...


class Foo:
    bar: BarType


