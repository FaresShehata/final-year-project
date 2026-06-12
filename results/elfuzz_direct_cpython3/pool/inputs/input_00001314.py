"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
S = TypeVar("S")


class MyEnum(enum.Enum):
    A = "a"
    B = "b"


# https://docs.python.org/3/library/dataclasses.html


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    address: Address


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str


p1 = Person(name="Alice", age=18, address=Address(street="Avenue U", city="Paris"))
print(p1.name)


class AsyncDataClass(Protocol[K, V]):
    def to_dict(self) -> dict[K, V]:
        ...


# https://docs.python.org/3/library/typing.html#typing.Protocol

class SupportsGetItem(AsyncDataClass[K, V]):
    async def get_item(self, key: K) -> V:
        raise NotImplementedError()


# https://www.python.org/dev/peps/pep-0484/#generic-types

_T_co = TypeVar("_T_co", covariant=True)


class SupportsAddition(Generic[_T_co] & Protocol):
    def __add__(self, other: _T_co | int | float | str) -> Self:
        ...


class SupportsSubtraction(SupportsAddition[float]):
    def __sub__(self, other: float) -> Self:
        ...


# https://www.python.org/dev/peps/pep-0655/


class SupportsSubtractionWithInv(TypedDict, total=False):
    minus_one: int
    minus_five: int
    minus_nine: int


class SupportsMultiplicationWithInv(TypedDict, total=False):
    times_two: int
    times_four: int
    times_eight: int


class SupportsDivisionWithInv(TypedDict, total=False):
    divided_by_three: int
    divided_by_six: int
    divided_by_eleven: int


class SupportsModuloWithInv(TypedDict, total=False):
    modulo_with_ten: int
    modulo_with_twenty: int
    modulo_with_thirty: int


class SupportsPowerWithInv(TypedDict, total=False):
    raised_to_the_power_of_two: int
    raised_to_the_power_of_three: int
    raised_to_the_power_of_four: int


class SupportsBooleanWithInv(TypedDict, total=False):
    equal_to_zero: bool
    greater_than_or_equal_to_zero: bool
    less_than_or_equal_to_zero: bool


class SupportsComparisonWithInv(TypedDict, total=False):
    less_than_one: bool
    less_than_or_equal_to_one: bool
    greater_than_one: bool
    greater_than_or_equal_to_one: bool


class StandardTypesWithInv(TypedDict, total=False):
    any_type: Any
    bytes: bytes
    complex_number: complex
    datetime.datetime: datetime.datetime
    datetime.date: datetime.date
    datetime.time: datetime.time
    decimal.Decimal: decimal.Decimal
    fractions.Fraction: Fraction
    frozenset: FrozenSet
    int: int
    list: List
    range: Range
    set: Set
    slice: Slice
    tuple:        ...
    @overload
    def __add__(self, other: int) -> Self:
        ...
    @overload
    def __add__(self, other: float) -> Self:
        ...
    @overload
    def __add__(self, other: str) -> str:
        ...


class ExampleSupportsAddition(SupportsAddition[int], Generic[T_co]):
    def __init__(self, a: T_co) -> None:
        self.a = a

    def __add__(self, other: T_co | None) -> Self:
        if other is not None:
            return self.__class__(self.a + other)

    def __radd__(self, other: Self) -> Self:
        return self.__add__(other.a)

    def __iadd__(self, other: Self) -> Self:
        return self.__class__(self.a + other.a)

    def __str__(self) -> str:
        return f"{self.a}"


# https://www.python.org/dev/peps/pep-0593/

def add_one(x: int | float) -> int | float:
    return x + 1.0


# https://github.com/python/mypy/issues/6789


async def func() -> None:
    await asyncio.sleep(1)
    print("hello world