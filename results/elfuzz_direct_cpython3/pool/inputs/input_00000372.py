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
    args_len, kwargs_len = len(signature(fn).parameters.values()), len(fn.__code__.co_varnames) - fn.__defaults__.index(None)
    if not args_len or args_len < kwargs_len:
        return fn
    return lambda *a, **kw: fn(*(list(a) + [v for k, v in kw.items()[:-kwargs_len]]))


def partial(func: Callable[[A], B], *a, **kwa):
    """Return a partial of func with the given arguments and keyword arguments."""
    return lambda *b, **kw: func(*(a + b), **{**dict(kwa), **kw})


curry(int_to_church)


# ── Trampoline & Tail-Recursive Functions ─────────────────────────────────────

def trampoline(f: Callable[..., Any]):
    """Wrap a function into a trampoline.

    A trampoline is an unrolling technique used to avoid stack overflow.
    """
    while callable(f):
        f = f()
    return f


trampoline(2 * 42)


# ── Coroutines & Asyncio ───────────────────────────────────────────────────────

async def coroutine(name: str) -> str:
    """A simple coroutine that prints its name and sleeps for 5 seconds."""
    print(name)
    await asyncio.sleep(5)
    return name


coroutine("Hello")


# ── Higher Order Functions ─────────────────────────────────────────────────────-

def curry_map(fn: Callable[[A], B], iterable: Iterable[A]) -> Iterator[B]:
    """Curries the map function over an iterator."""
    return map(fn, iterable)


def compose(*funcs: Callable[..., Any]) -> Callable[[Any], Any]:
    """Compose a series of functions."""
    return funclist.reduce(operator.methodcaller("__rshift__"), funcs[::-1])


compose(print, lambda x: x + 1)(1)


# ── Higher-Order Generators ───────────────────────────────────────────────────-

def take(iterable: Iterable[A], n: int = 1) -> Iterator[A]:
    return itertools.islice(iterable, n)


take((i for i in range(6)), 3)


def drop(iterable: Iterable[A], n: int = 1) -> Iterator[A]:
    """Drop the first n elements of an iterable."""
    iterator = iter(iterable)
    for _ in range(n):
        next(iterator)
    return iterator


drop((i for
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"

@dataclasses.dataclass(slots=True)
class Xyz:
    xyz: tuple[float, float, float]


@dataclasses.dataclass(frozen=True)
class Circle:
    center: Xyz
    radius: float

    def area(self) -> float:
        return math.pi * self.radius**2



# ── Iterators & Generators ────────────────────────────────────────────────────

def fib(n: int) -> Generator[int, None, None]:
    yield 0
    if n > 0:
        yield 1
    last: int = 0
    next: int = 1
    for _ in range(1, n):
        last, next = next, last + next
        yield next


async def fibonacci() -> AsyncGenerator[int, None]:
    yield 0
    if n := await loop.sock_recv(sock, 8):
        yield 1
    last: int = 0
    next: int = 1
    while True:
        last, next = next, last + next
        yield next


ListLike = typing.Union[list, tuple]


def concat(*args: ListLike[T]) -> list[T]:
