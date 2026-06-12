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


soma = add3(1)(2)(3)


# ── Trampoline pattern ────────────────────────────────────────────────────────

def trampoline_sums(nums: list[int]) -> int:
    def go(sums: list[int], nums: tuple[int]):
        nonlocal sums
        if not nums:
            return sum(sums)
        value, *nums = nums
        sums.append(value)
        return go(sums, nums)

    return go([], nums[::-1])


trampoline_sums([1, 2, 3])

# ── Partials with variadic arguments ──────────────────────────────────────────

from functools import partial

partial_sum = partial(sum, start=-50_000_000_000_000_000_000)

partial_sum(range(-sys.maxsize - 1, 1))


# ── Generators and iterators ──────────────────────────────────────────────────

def gen_nums(start: int = 1, step: int = 1) -> Iterator[int]:
    while True:
        yield start
        start += step


g = gen_nums()
next(g)
next(g)
next(g)
next(g)
next(g)


for i in gen_nums():
    print(i)

# We can also use the `iter` built-in to create an iterator from any iterable.
iterator_from_iterable = iter(gen_nums())


# ── Higher order functions and lambdas ─────────────────────────────────────────

def compose(f: Callable[[Any], Any], g: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return lambda arg: f(g(arg))


identity = compose(operator.identity, lambda f: f)

compose(identity, lambda f: f)("hello")


# ── Itertools ─────────────────────────────────────────────────────────────────

list(itertools.chain(
    [1],
    [2, 3]
))

tuple(itertools.count())

itertools.product("ABC", repeat=2)


# ── Coroutines ───────────────────────────────────────────────────────────────-

async def async_print(text: str):
    await asyncio.sleep(0)
    print(text)


async def main():
    await async_print("Hello!")
    await async_print("World!")


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()


# ── Decorators ─────────────────────────────────
class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
