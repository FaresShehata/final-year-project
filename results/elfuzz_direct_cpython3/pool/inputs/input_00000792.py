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
        case {**kwargs}:
            return False
        case dict(name=str, **_):
            return True
        case _:  # Fallthrough to default.
            return False


# https://www.youtube.com/watch?v=XH4rQn9x5WU
# https://youtu.be/XH4rQn9x5WU?t=868
async def sleep_and_print(i) -> None:
    await asyncio.sleep(random.random())
    print(f"sleep_and_print({i})")


async def main():
    for i in range(10):
        await sleep_and_print(i)

    my_slots_dc = ExampleSlotsDataClass("John Doe", 25)
    assert my_slots_dc.name == "John Doe"
    assert my_slots_dc.age is None

    print(match_example({"name": "John"}))
    print(match_example(dict(name="John")))
    print(match_example({"age": 25}))
    print(match_example("Hello World"))

    match_example(None)

    # https://stackoverflow.com/questions/62826708/how-to-use-runtime-checkable-with-custom-types
    class Annotated(typing.Generic[_T], typing._AnnotatedAlias):  # type: ignore[attr-defined]
        """Generic annotation type."""

    <|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    if origin != Annotated:
        raise ValueError("Must be an 'Annotated' type.")

   