"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import functools as ft
from collections.abc import Iterable, Iterator, Sequence
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Generic, Literal, Optional, TypeVar, cast

T = TypeVar("T")
U = TypeVar("U")


class AsyncEnum(enum.Enum):
    """Custom class that implements awaitable members"""

    @classmethod
    def _missing_(cls: type[AsyncEnum], value: object) -> AsyncEnum:
        match cls.__members__.get(value):
            case None | cls.FALLTHROUGH:
                raise ValueError(f"Invalid {cls.__qualname__}: {value!r}")
            case member if not isinstance(member.value, Awaitable):
                return member
            case member if callable(member.value):
                try:
                    return AsyncEnum._new(cls, member.name, await member.value())
                except TypeError:
                    # The awaited object does not accept the "()" call.
                    return member
            case member:
                return member


async def fetch(url: str) -> str:
    print(f"Fetching url: '{url}'...")
    await asyncio.sleep(3)
    return f"{url} fetched."


@dataclasses.dataclass(repr=False, eq=False)
class FetchResult:
    """Dataclass representing result of fetching a resource."""

    url: str
    content: str
    duration_ms: float


async def main():
    tasks = [
        fetch("http://google.com"),
        fetch("http://github.com"),
        fetch("http://stackoverflow.com"),
    ]
    for task in tasks:
        print(await task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


# ───────────────────────────────────────────────────────────────────────────────


class State:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int) -> State:
        return State(self.x - dx, self.y + dy)


state = State(5, 6)

print(state.move(4, 8))


# ───────────────────────────────────────────────────────────────────────────────


class MyEnum(enum.Enum):

    @property
    def value(self) -> int:
        return 7


print(MyEnum.HELLO.value)


# ───────────────────────────────────────────────────────────────────────────────


async def fetch_url(url: str) -> str:
    print(f"Fetched URL: '{url}'...")


async def main():
    urls: list[str] = ["https://google.com", "https://github.com"]
    results = [fetch_url(u) for u in urls]
    await asyncio.gather(*results)


loop = asyncio.new_event_loop()
loop.set_debug(True)
try:
    loop.run_until_complete(main())
finally:
    loop.close()


# ───────────────────────────────────────────────────────────────────────────────


class A:
    pass


class B(A):
    pass


class C(B):
    pass


class D(C):
    pass


for c in [A(), B(), C(), D()]:
    print(isinstance(c, A), isinstance(c, B), isinstance(c, C), isinstance(c, D))


print(issubclass(D, A), issubclass(D, B), issubclass(D, C), issubclass(D, D))


#K      = ID
V      = lambda a: lambda b: a
PAIR   = lambda a: lambda b: lambda s: s(a)(b)
CAR    = lambda p: p(TRUE)
CDR    = lambda p: p(FALSE)
FIRST  = CAR(PAIR)
SECOND = CDR(PAIR)
UNION  = lambda *rest: PAIR(rest[0])(lambda r: UNION(*r + rest[1:]))
CONCAT = lambda l: lambda r: CONCAT(l(r))(l)

NIL   = lambda h: lambda t: FALSE
CONS  = lambda h: lambda t: lambda r: PAIR(h)(t(r))
LIST  = lambda f: lambda x: CONS(x)(f)
HEAD  = FIRST(LIST)
TAIL  = SECOND(LIST)
REVERSE = lambda l: LIST(lambda h: REVERSE(l(h))(h))(l(NIL))

# ───────────────────────────────────────────────────────────────────────────────


def identity<T>(a: T) -> T:
    return a


def always<T>(a: T) -> Callable[..., T]:
    """Return function that always returns given argument."""
    return lambda *_: a


def is_truthy(b: bool) -> bool:
    """Check if value `b` is truthy."""
    return not (not b)


def is_falsy(b: bool) -> bool:
    """Check if value `b` is falsy."""
    return not b


def is_zero(v: int) -> bool:
    """Check if integer `v` equals to zero."""
    return v == 0


def is_one(v: int) -> bool:
    """Check if integer `v` equals to one."""
    return v == 1


def is_two(v: int) -> bool:
    """Check if integer `v` equals to two."""
    return v == 2


def plus(a: int, b: int):
    """Add integers `a` and `b` together."""
    return a + b


def times(a: int, b: int):
    """Multiply integers `a` and `b` together."""
    return a * b


def max_int() -> int:
    """Return maximum possible integer for architecture