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


# https://peps.python.org/pep-3107/
@typing.runtime_checkable
class Protocol(typing.Protocol):
    @staticmethod
    def method() -> str:
        ...


# https://realpython.com/python-dataclasses/#slots
@dataclasses.dataclass(slots=True)
class ExampleSlotsDataClass:
    name: str
    age: int | None = None


# https://pythonspeed.com/articles/structural-pattern-matching-python/
def match_example(input_value) -> bool:
    match input_value:
        case {"name": _}:
            return True
        case _:
            return False


# https://www.youtube.com/watch?v=rhIyWgOxXDE
print("walrus")
while value := (yield from example_async()):
    pass

# https://peps.python.org/pep-0589/
try:
    raise ValueError("ExampleValueError")
except Exception as e:
    for exc in e.__cause__:
        print(exc)

# https://docs.python.org/3/library/typing.html#generics
T = typing.TypeVar("T")


class GenericMethod(typing.Generic[T]):
    def __init__(self) -> None:
        self.value: T = None

    def set(self, x: T):
        self.value = x

    def get(self) -> T:
        return self.value


if __name__ == "__main__":
    example_async()

    # https://github.com/samuelcolvin/pydantic/issues/3134
    class ExamplePydanticModel(pydantic.BaseModel):
        name: str
        age: int | None = None


    model_instance = ExamplePydanticModel(name="John Doe", age=30)
    print(model_instance.dict())