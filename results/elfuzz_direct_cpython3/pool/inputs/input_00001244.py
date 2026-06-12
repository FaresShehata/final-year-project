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


def print_(*args: A | B | C) -> None:
    """
    >>> print_("foo", "bar", sep=" ")
    foo bar
    """
    print(" ".join(map(str, args)))


def plus(n1: int, n2: int) -> int:
    return n1 + n2


print_(plus(1, 2))  # 3


# Closure example
def make_incrementor(n: int) -> Callable[[int], int]:
    def inc(x: int) -> int:
        return x + n

    return inc


inc_by_one = make_incrementor(1)
inc_by_ten = make_incrementor(10)

assert inc_by_one(4) == 5
assert inc_by_ten(4) == 14


# Higher-order function example
def sum_of_squares(numbers: list[int]) -> int:
    return sum(map(lambda n: n * n, numbers))


assert sum_of_squares([1, 2, 3]) == 14


# Comprehension example
[(x, y) for x in range(3) for y in range(2)]
[(x, y) for x in range(3)]  # <- only one `y` iteration possible


# Generator expression example
generator_expression = (x ** 2 for x in range(3))
next(generator_expression)  # 0
next(generator_expression)  # 1
next(generator_expression)  # 4
next(generator_expression)  # StopIteration exception


def count_to(limit: int) -> Iterator[int]:
    current_number = 0
    while current_number < limit:
        yield current_number
        current_number += 1


count_generator = count_to(5)
for number in count_generator:
    print(number, end=" ")  # 0 1 2 3 4
    assert next(count_generator) == 5


# Generator example
def fibs() -> Generator[int, None, None]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


fibs_generator = fibs()

assert next(fibs_generator) == 0
assert next(fibs_generator) == 1
assert next(fibs_generator) == 1
assert next(fibs_generator) == 2
assert next(fibs_generator) == 3
assert next(fibs_generator) == 5


# Coroutine example
async def main():
    async with (
        StreamReader() as reader,
        StreamWriter() as writer,
    ):
        task = asyncio.create_task(reader.read_until(b"q"))
        writer.write("hello".encode())

        _, data = await asyncio.gather(task, writer.drain())
        assert data.decode().strip() == "hello"


# Corouting send/throw/close examples
async def async_coroutine() -> int:
    try:
        value = await some_function()
        return value
    except Exception as e:
        raise ValueError from e


async def example_with_close():
    async with open("example.txt") as f:
        await f.readline()


async def example_with_send_and_throw():
    async with (StreamReader(), StreamWriter()) as (reader, writer):
        writer.transport.send_nowait("some data")

        await writer.wait_closed()


# Itertools examples
list(itertools.chain(range(6), reversed(range(6))))

list(itertools.starmap(pow, zip(range(8), [3] * 8)))

list(itertools.islice(filter(bool, map(len, ["a", "b"])), 3))

list(itertools.conijoin(["a", "b"], repeat=2))

list(itertools.product("ABCD"))

dict(zip(("a", "b"), (1, 2)))

dict.fromkeys("ab", 3)

set.union({"a"}, {"b"})


# functools examples
functools.reduce(operator.add, [1, 2, 3])


# Lambda calculus encoding
(lambda x: lambda y: x + y)(1)(2)  # 3
(lambda x: lambda y: x + y)(1)(lambda z: z + 1)(2)  # 4


# Currying
def curry(func: Callable[..., any]):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = inspect.signature(func).bind_partial(*args, **kwargs)
        return lambda rest_args: func(**bound_args.arguments, **rest_args)

    return wrapper


curried_sum = curry(sum)
sum_five = curried_sum(5)
assert sum_five(2, 3) == 8


# Partial application
partial_curry = functools.partial(curry, sum)
sum_five = partial_curry(5)
assert sum_five(2, 3) == 8


# Trampolines
trampoline = lambda f: lambda *args, _i=None: f(trampoline(f))(args, _i or 0) if _i else f(args, _i)[0]
long_chain_trampolined_function = trampoline(long_chain_function)
result = long_chain_trampolined_function()


# Dataclasses
@dataclasses.dataclass    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str


@dataclasses.dataclass(frozen=False)
class Planet:
    name: str
    moons: tuple[str, ...]


@dataclasses.dataclass(order=True, frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str


@dataclasses.dataclass(eq=True, order=True, frozen=True)
class Employee(Person):
    department: str
    salary: float


@dataclasses.dataclass(order=True, frozen=True)
class Card:
    number: int
    issuer: str
    balance: float


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotUser:
    name: str
    age: int


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_pattern(value: T, patterns: list[tuple[Callable[[T], bool], Callable[[T], V]]] | None = None) -> V:
    if not isinstance(patterns, list):
        patterns = [(lambda _: True, lambda x: x)]

    for is_match, transform in patterns:
        if is_match(value):
            return transform(value)


def match_type(obj: object, types: list[type[T]]) -> bool | V | None:
    for t in types:
        if isinstance(obj, t):
            return t()

    return False


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def do_something() -> None:
    print(await asyncio.sleep(random.random()))


async def main():
    await do_something()


# ── Generics ──────────────────────────────────────────────────────────────────

@overload
def get_most_common(items: list[V], k: Literal[0]) -> dict[V, int]: ...
@overload
def get_most_common(items: list[V], k: int) -> list[tuple[V, int]]: ...


def get_most_common(
