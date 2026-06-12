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
    def wrapped(*args):
        if len(args) < arity:
            return curry(wrapped)
        else:
            return fn(*args)

    return wrapped

@curry
def add(a: A, b: B) -> C:
    return a + b
add(3)(4)


def compose(*fs: Callable[[Any]], **kwargs: Callable[[], Any]) -> Callable[..., Any]:
    """
    Compose arbitrary number of functions. Returns the composition of arguments.

    >>> f = compose(print, print, print)
    >>> f(2, 3, 5)
    2
    3
    5

    If you want a single output argument instead of all outputs,
    use ``*`` to unpack the sequence into positional arguments.
    You can also specify keyword-only args with ``**``:

    >>> g = compose(add, subtract, multiply, divide, add, subtract, multiply, divide)
    >>> g(3, 7, a=8, b=4, c=2)
    9
    6
    4
    3

    :param fs: Functions to compose.
    :param kwargs: Keyword-only arguments to pass on to each function.
    :return: The composed function.
    """

    def inner(*args, **kwargs):
        res = fs[-1](*args, **kwargs)
        for f in reversed(fs[:-1]):
            res = f(res)
        return res

    return inner


compose(int, str, chr)(*range(ord('a'), ord('z')))


def partial(func: Callable, /, *args, **kwargs) -> Callable:
    """
    Partially apply some arguments to a callable without a fixed return type.

    This works by returning a new function which receives only the remaining arguments.
    If this function is called again with fewer arguments than the original one,
    it will be partially applied again until no more arguments are left or an exception occurs.

    Note that this does not work with variable-length arguments (`*`), keyword arguments (`**`),
    or default arguments because we need to know their values at compile-time.

    >>> def foo(x, y, z, w, v):
    ...     return x + y - z * v
    >>> f = partial(foo, 1, 2, 3)
    >>> f(4)
    3
    >>> f(5)
    0
    >>> f(6)
    -3
    >>> f(7)
    -6
    >>> f(8)
    -9
    >>> f(v=9)
    3
    >>> f(10, v=-10)
    -10
    >>> f
# ── Generics ─────────────────────────────────────────────────────────────────
TypeVar
Generic[T]
re.sub(r"\b[a-z]+\b", lambda m: m.group().upper(), string)


# ── Async ───────────────────────────────────────────────────────────────────-

async def sleep(n: int | float) -> None:
    await asyncio.sleep(n)


async def coroutine_with_yield_from() -> int:
    yield from range(10)
    return sum(range(10))

coroutine_with_yield_from()


# ── Exceptions ───────────────────────────────────────────────────────────────

try:
    ...
except ZeroDivisionError as e:
    print(e.__str__())  # repr()
    print(repr(e))      # str()
    print(e.args)       # tuple(args)
except (TypeError, RuntimeError) as e:
    print(type(e))
else:
    print("no error")


class MyException(Exception):
    def __init__(self, *args: object) -> None:
        pass


ex: MyException = MyException()
print(ex.args        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
