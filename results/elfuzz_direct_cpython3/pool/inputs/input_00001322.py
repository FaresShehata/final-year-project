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

K = TypeVar("K")  # key type
V = TypeVar("V")  # value type


class AsyncGenerator(Generic[K, V], Awaitable[Iterator[V]], Protocol):
    """Async generator protocol."""

    def __aiter__(self) -> AsyncGenerator[K, V]:
        ...


@overload
def filter(iterable: AsyncGenerator[K, V]) -> AsyncGenerator[K, V]:  ...
@overload
def filter(
    iterable: Iterable[K],
    predicate: Callable[[K], bool] | None = ...,
) -> Iterator[V]:  ...
def filter(
    iterable: Iterable[K],
    predicate: Callable[[K], bool] | None = None,
) -> Iterator[V] | AsyncGenerator[K, V]:  # noqa: E301, F811, RUF100
    if isinstance(iterable, AsyncGenerator):
        return (x for x in iterable if predicate(x) if predicate is not None)
    return (x for x in iterable if predicate(x) if predicate is not None)


@runtime_checkable
class SupportsLessThan(Protocol):
    """Supports less than comparison."""

    def __lt__(self, other: object) -> bool:  # noqa: A003
        ...


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int

    @property
    def is_adult(self) -> bool:  # property used as a descriptor
        return self.age >= 18


# with slots attribute the class does not allow adding new attributes
@dataclasses.dataclass(slots=True, frozen=False)
class Point:
    x: float
    y: float


@dataclasses.dataclass()
class DataClassDemo:
    """Data classes demo."""

    count: int = dataclasses.field(default=0)
    text: str = "text"
    num: list[int] = dataclasses.field(default_factory=list)
    points: tuple[float] = dataclasses.field(default_factory=tuple)

    def add_num(self, n: int):
        self.num.append(n)

    def add_tuple(self, t: Tuple[int]):
        self.points += t

    def add_data_class(self, dc: DataClassDemo):
        self.count += dc.count


# this is useful when working with JSON data
data_json = '{"json": true}'


def dump_json(data: dict[str, Any]):
    print(json.dumps(data, indent=4))


dump_json(json.loads(data_json))  # prints {"json": true}
# it's possible to make sure that JSON objects are properly read into Python types
print(json.loads(data_json, object_hook=lambda d: {k: v for k, v in d.items()}))

# convert dictionary into JsonDict
import json

JsonDict = Dict[str, Union[bool, float, int, str]]  # noqa: N806


def get_dict_from_json() -> JsonDict:
    return json.loads(data_json, object_hook=lambda d: {k: v for k, v in d.items()})


# with walrus operator
async def get_user(user_id: int) -> User:
    user_info = await fetch_user_info(user_id)
    profile