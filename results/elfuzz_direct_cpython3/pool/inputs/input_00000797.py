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
                    # We look for a method with the name "__call__".
                    return member


class AsyncAwaitable(AsyncEnum):
    FALLTHROUGH = object()

    def __await__(self) -> Generator[Any, None, Any]:
        yield self.value


@dataclasses.dataclass(slots=True)
class DataClass:
    """A simple class with custom slots and a custom __init__."""

    slot1: int
    slots: tuple[int] = ()


def some_awaitable_function() -> str:
    """Some example function that returns a string."""
    return "Hello World!"


async def my_async_function(a: AsyncAwaitable[str]) -> None:
    """Example of an asynchronous function that takes an optional parameter."""
    print(await a)


# -----------------------------------------------------------------------------
#
#                               SEED 2: ASYNC/AWAIT
#
# -----------------------------------------------------------------------------

async def main():
    """Main function to demonstrate using the provided functions."""

    async with AsyncAwaitable(FALLTHROUGH) as f:
        assert f == AsyncAwaitable.FALLTHROUGH

    async with AsyncAwaitable.some_awaitable_function() as f:
        assert f == some_awaitable_function()

    await my_async_function(AsyncAwaitable(some_awaitable_function()))


if __name__ == "__main__":
    asyncio.run(main())

# -----------------------------------------------------------------------------
#
#                               SEED 3: PROTOCOLS
#
# -----------------------------------------------------------------------------


class IComparableProtocol(Generic[T]):
    """A protocol defining comparison operations."""

