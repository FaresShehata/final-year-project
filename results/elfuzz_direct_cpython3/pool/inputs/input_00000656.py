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
import logging
import pickle
import random
import re
import sys
import timeit
import types
import typing


# https://cs.wikipedia.org/wiki/Asyncio
async def example_async():
    print(f"{example_async=}")


# https://docs.python.org/3/library/enum.html
class ExampleEnum(enum.Enum):
    a = "a"
    b = "b"


# https://docs.python.org/3.6/library/dataclasses.html
@dataclasses.dataclass()
class ExampleDataClass:
    name: str
    age: int | None = None


# https://peps.python.org/pep-0565/
def my_function(a: (int, float)):
    pass


# https://github.com/python/mypy/issues/7389
T = typing.TypeVar("T")
U = typing.TypeVar("U")


def my_generic_function(x: T) -> U:
    return x


# https://stackoverflow.com/a/64518532
def my_generic_class[T](value: T) -> T:
    return value


my_generic_instance = my_generic_class[object]("foo")

try:
    import numpy as np  # type: ignore
except ModuleNotFoundError:

    class _ArrayLike(typing.Protocol):  # type: ignore

        @property
        def shape(self) -> tuple[int]:
            ...

    class ArrayLike(_ArrayLike):

        @typing.overload
        def __getitem__(self, index: slice) -> ArrayLike:  # type: ignore  # noqa: E501
            ...

        @typing.overload
        def __getitem__(
            self, index: int
        ) -> Union[float, ArrayLike]:  # type: ignore
            ...

        @typing.overload
        def __getitem__(self, index: _ArrayLike) -> ArrayLike:
            ...

        def __getitem__(self, index: ...) -> ArrayLike:
            ...

    class Array(ArrayLike):

        def __init__(self, array_like: ArrayLike):
            self.array_like = array_like

        @property
        def shape(self) -> tuple[int]:
            return (
                len(self),
                *map(len, zip(*((self[i] if i < len(self) else ()) for i in range(0, len(self), 2)))),
            )

        def __len__(self) -> int:
            return len(self.array_like)

        for k, v in items:
            lines.append(
                f"    {k:{max_key_len}} : {v!r},"
            )
        lines[-1] = lines[-1][:-1]  # remove final comma
        lines.append("}")
    return "\n".join(lines)


