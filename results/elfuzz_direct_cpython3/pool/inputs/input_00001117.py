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

        def __getitem__(self, index: ...) -> ArrayLike:  # type: ignore
            ...

    class Array(np.ndarray[_ArrayLike]):  # type: ignore
        pass

    class Matrix(ArrayLike):  # type: ignore
        pass


# https://www.pythontutorial.net/python-basics/python-structural-patterns/
def transfer_data(data: dict[str, any]) -> None:
    match data:
        case {"name": _, "age": _, **_}:
            print("match on `dict`")
        case (_ : str, _: int, **_):
            print("match on `tuple`")
        case _:
            print("default")


# https://realpython.com/python-typing/#the-new-and-improved-python-type-hints-system
def transfer_data_typed(data: dict[str, any]) -> None:
    match data:
        case {"name": _, "age": _, **_}:
            print("match on `dict`")
        case (_ : str, _: int, **_):
            print("match on `tuple`")
        case _:
            print("default")


def transfer_data_json(data: dict[str, any]) -> None:
    try:
        transfer_data(json.loads(pickle.dumps(data)))
    except Exception as e:
        raise ValueError from e


transfer_data_typed({"name": "Alice", "age": 30})
transfer_data_typed((1, "Alice", 30))
transfer_data_typed({})


# https://docs.python.org/3/library/types.html
def is_type(obj: object) -> bool:
    if not isinstance(obj, types.GenericAlias):
        return False
    if obj.__origin__ == list or obj.__origin__ == tuple:
        return True
    if obj.__args__[0] in [str, int, float, complex, bytes, bytearray, memoryview]:
        return True
    if obj.__args__[-1] in [
        str,
        int,
        float,
        complex,
        bytes,
        bytearray,
        memoryview,
    ] and len(obj.__args__) > 2:
        return True
    return False


assert is_type(list(str))
assert is_type(tuple(int))
assert is_type(list(str, str))
assert is_type(list(str, int))
assert is_type(tuple(str, int))


# https://www.burgaud.com/walrus-operator-in-python/
def main() -> None:
    for i in