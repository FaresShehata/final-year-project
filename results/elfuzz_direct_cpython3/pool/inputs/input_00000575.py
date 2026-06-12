"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import collections
import enum
import inspect
import json
import logging
import os
import random
import re
import string
import time
import uuid
from datetime import date, datetime, timedelta
from functools import cached_property
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Pattern,
    Tuple,
    Type,
    TypeVar,
    Union,
)

import aiofiles
import aiosqlite
import attrs
import pydantic
from attrs.converters import from_iterable


def run(func: Callable[..., Awaitable[Any]]) -> None:
    """
    Run a coroutine function and print the result.

        >>> def func() -> int:
        ...     return 42
        ...
        >>> run(func)
        42
    """

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.create_task(func()))


class DateRange(NamedTuple):
    """A named tuple representing a range of dates."""

    start_date: date
    end_date: date


class Range(NamedTuple):
    """A named tuple representing a range of numbers."""

    start: int
    end: int


def get_unique_names(start_index: int) -> Generator[str, None, None]:
    """Return an infinite sequence of unique names starting at `start_index`."""
    index = start_index
    while True:
        yield str(index).zfill(8)
        index += 1


@attrs.define(auto_attribs=True)
class Person:
    name: str
    age: int
    email: str
    phone_number: str = "unknown"
    address: str = ""

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.age}"

    @classmethod
    def create(cls, **kwargs: Any) -> Person:
        return cls(**dict(kwargs))

    @cached_property
    def is_adult(self) -> bool:
        return self.age >= 18

    def greet(self, *args: Any, **kwargs: Any) -> None:
        print(f"Hello, my name is {self.full_name}")

    def say_hello(self, message: str) -> None:
        print(message)


async def main():
    async with aiosqlite.connect(":memory:") as conn:
        await conn.execute(
            "CREATE