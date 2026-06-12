"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
from collections.abc import Callable, Iterable
from typing import Any, Awaitable, AwaitableTypeVar, TypeVar

V = TypeVar("V")
A = TypeVar("A", covariant=True)
B = TypeVar("B")

# ── Closures ──────────────────────────────────────────────────────────────────


def closure_example() -> Callable[[int], str]:
    s = "Hello"

    def hello(name: str) -> str:
        return s + ", " + name

    return hello


hello_world = closure_example()

print(hello_world("World")) # => "Hello, World"


# ── Higher order functions and comprehensions ──────────────────────────────────


def add_one(x: int) -> int:
    return x + 1

numbers = [i for i in range(10)]
doubled_numbers = [number * 2 for number in numbers]
added_one = map(add_one, numbers)

mixed_list = [(item := item, id(item)) for item in doubled_numbers]

for item in mixed_list:
    print(item)

assert item == (10, object())

# ── Generator functions ───────────────────────────────────────────────────────


async def async_generator() -> AsyncGenerator[int, None]:
    num = 0
    while True:
        await asyncio.sleep(0)
        num += 1
        yield num


async def main():
    async for number in async_generator():
        print(number)


# ── Coroutines ────────────────────────────────────────────────────────────────


async def add_coroutine(first: int, second: int) -> int:
    return first + second


async def subtract_coroutine(first: int, second: int) -> int:
    return first - second


async def multiply_coroutine(first: int, second: int) -> int:
    return first * second


async def divide_coroutine(first: int, second: int) -> float:
    return first / second


async def execute_coroutine(coroutine_name: str, *coroutines: Coroutine) -> None:
    match coroutine_name.lower():
        case "add":
            async with contextlib.suppress(TypeError):
                total = await functools.reduce(add_coroutine, coroutines)
                print(total)
        case "subtract":
            async with contextlib.suppress(TypeError):
                total = await functools.reduce(subtract_coroutine, coroutines)
                print(total)
        case "multiply":
            async with context# ── Lambda-calculus church encodings ─────────────────────────────────────────

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


print(add3(1)(2)(3)) # => 6

# ── Partial application
add_5  = add3(5)
add_42 = add3(42)

print(add_5(7)) # => 12
print(add_42(-19)) # => 23


# ── Trampolines ───────────────────────────────────────────────────────────────

class Thunk(Callable[[], A]):
    def __init__(self, func: Callable[[Thunk[A]], A], args: tuple[Any] | None):
        self.func = func
        self.args = args or ()

    def __call__(self):  # pragma: no cover
        try:
            return self.func(self)(*self.args)
        except RecursionError as e:
            raise RuntimeError(
                "you have recursed too deep; try using a trampoline"
            ) from e


def trampoline(func: Callable[..., A]) -> Callable[[Thunk[A], ...], A]:
    """Trampoline decorator."""

    @functools.wraps(func)
    def trampolined(*args, **kwargs):
        thunk = Thunk(func, args)
        while isinstance(thunk, Thunk):
            thunk = thunk()
        return thunk

    return trampolined


@trampoline
def factorial(n: int) -> int:
    if not n:
        return 1
    return n * factorial(n - 1)


assert factorial(8) == 40320


# ── Combinators ───────────────────────────────────────────────────────────────

def compose(functions: list[Callable]) -> Callable:
    """Compose the given sequence of functions, left-to-right."""
    funcs = iter(functions)
    first = next(funcs)
    return lambda *args: first(compose(list(funcs))(tuple(args)))


def identity(x: Any) -> Any:
    return x


compose([identity]) == identity
compose([lambda x: x ** 2, lambda y: y * 3])((1, 2))


# ── Lambdas ───────────────────────────────────────────────────────────────────

lam_add = lambda a, b: a + b
lam_mul = lambda a, b: a * b

bound_lam_add = lam_add.bind(lam_add)
bound_lam_mul = lam_mul.bind(lam_mul)

# lambdas are closures, see `test_bound_lambda`
value = bound_lam_add(5, 3)
assert value == 8


# ── Misc ─────────────────────────────────────────────────────────────────────-

# The following is adapted from https://stackoverflow.com/a/4805272/17655050
def coroutine(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Transform any generator-based coroutine into a regular callable.
    """

    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


def coroutine_with_yield_from():
    yield from range(10)


