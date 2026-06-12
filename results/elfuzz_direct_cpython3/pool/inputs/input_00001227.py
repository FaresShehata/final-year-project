"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

import functools
from typing import List, Tuple, Any, Union, Hashable, Callable, Optional
import math
from collections import deque
from dataclasses import dataclass
from decimal import Decimal


# 1. Closures
def make_counter(start: int = 0) -> Callable:
    count = [start]

    def inc() -> None:
        nonlocal count
        count[0] += 1

    def reset() -> None:
        nonlocal count
        count[0] = start

    def get_count() -> int:
        nonlocal count
        return count[0]

    inc.reset = reset  # type: ignore[attr-defined]
    inc.get_count = get_count  # type: ignore[attr-defined]
    return inc


def make_incrementor(n: int) -> Callable:
    return lambda x: x + n


def make_increase_by_2() -> Callable:
    f = make_incrementor(2)

    def increase_by_two(v: int) -> int:
        return f(v)

    return increase_by_two


def make_circular_list(seq: Sequence[Any]) -> Callable:
    it = iter(seq)
    i = -1

    def next_item() -> Any:
        nonlocal i
        i += 1
        try:
            return seq[i]
        except IndexError:
            i = 0
            return seq[i]

    return next_item


@dataclass
class Cell(object):
    value: int

    def __add__(self, other: int) -> 'Cell':
        self.value += other
        return self

    def __sub__(self, other: int) -> 'Cell':
        self.value -= other
        return self

    def __mul__(self, other: int) -> 'Cell':
        self.value *= other
        return self

    def __floordiv__(self, other: int) -> 'Cell':
        self.value //= other
        return self

    def __mod__(self, other: int) -> 'Cell':
        self.value %= other
        return self

    def __truediv__(self, other: int) -> 'Cell':
        self.value /= other
        return self

    def __pow__(self, power: int, modulo=None) -> 'Cell':
        self.value **= power
        return self

    def __neg__(self) -> 'Cell':
        self.value *= -1
        return self


def        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def accumulate(value: float) -> float:
        nonlocal total
        total += value
        return total

    return accumulate


# 2. Higher-Order Functions
def square(x: int) -> int:
    return x**2


def map_function(func: Callable, iterable: Iterable) -> List:
    result: list = []
    for item in iterable:
        result.append(func(item))
    return result


def map_function_comprehension(
    func: Callable, iterable: Iterable
) -> List:
    return [func(item) for item in iterable]


def filter_function(iterable: Iterable, predicate: Callable) -> List:
    result: list = []
    for item in iterable:
        if predicate(item):
            result.append(item)
    return result


def filter_function_comprehension(
    iterable: Iterable, predicate: Callable
) -> List:
    return [item for item in iterable if predicate(item)]


def reduce_function(combiner: Callable, iterable: Iterable, initial: Any) -> Any:
    accumulator: Any = initial
    for item in iterable:
        accumulator = combiner(accumulator, item)
    return accumulator


# 3. Comprehensions and Generators
def comprehension_generator(num: int) -> Generator:
    yield num
    yield from comprehension_generator(num - 1)


def generator_expression(num: int) -> Generator:
    return (num for i in range(num))


def fibonacci_sequence(
    num: int, acc: Optional[Tuple[int, int]] = None
) -> Tuple[int, ...]:
    if not acc:
        acc = (0, 1)
    elif num == 0:
        return ()
    else:
        new_acc = (acc[1], acc[0] + acc[1])
        return (
            *fibonacci_sequence(num - 1, new_acc),
            new_acc[0],
        )


def fibonacci_sequence_map_reduce(acc: Optional[Tuple[int, int]] = None) -> int:
    if not acc:
        acc = (0, 1)
    elif acc[0] != 0 or acc[1] != 1:
        return sum(acc) % 2

    return fibonacci_sequence_map_reduce((acc[1], acc[0] + acc[1]))


def partition(pred: Callable, seq: Iterable) -> Tuple[list, list]:
    true: list = []
    false_: list = []

    for item in seq:
        if pred    foo: FooProtocol = Bar()
    print(foo.bar)

    # dataclasses
    @dataclass(frozen=True)
    class ADataclass:
        a: int
        b: str = "b"

    print(ADataclass(1, "a"))

    # __slots__
    class BSlot:
        __slots__ = ("a", "b")

        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

    # Structural Pattern Matching
    match x:
        case 1 | (2, 3):
            pass
        case [1 + y]:
            pass
        case {"key": val}:
            pass
        case {val if v > 0 for v in range(5)}:
            pass
        case _:
            pass

    # Walrus Operator
    print((x := 42))

    # typing generics
    from typing import List, Tuple

    from typing_extensions import Unpack

    def f(x: int | float, *args: complex, **kwargs: bool | str) -> List[Tuple[int, ...]]:
        ...

    def g(*args: Unpack[Tuple[List[float], ...]]) -> None:
        ...

    # exception groups
    import sys
    from contextlib import suppress

    with suppress(Exception):
        raise ValueError("foo")
    with suppress(ZeroDivisionError, OverflowError):
        1 / 0
    with suppress(TypeError, KeyError):
        {}["bar"]
    with suppress(ValueError, ZeroDivisionError) as excs:
        1 / 0
    with suppress(*sys.exc_info()) as excs:
        raise RuntimeError("oops!")

    group = ExceptionGroup(
        "group",
        [
            TypeError("arg"),
            RuntimeError("oops!"),
            SyntaxError("syntax error"),
        ],
    )
    print(group.exceptions)
    print(group.summary())
    print(group.with_tracebacks())

    # https://docs.python.org/3/library/exceptions.html#exception-groups
    try:
