"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc, dataclasses, enum, functools, itertools, math, operator, pathlib, random, re, typing, uuid as _uuid
from collections.abc import Sequence
from functools import singledispatch
from inspect import signature as sig
from numbers import Number
from typing import (
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterator,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
)

import numpy as np
import numpy.typing as npt
import numpy.random as nrnd
import pandas as pd
import PIL.Image as Image
from PIL.PngImagePlugin import PngInfo
from typing_extensions import Concatenate, ParamSpec, Self, TypeGuard, get_args, get_origin, overload

P = ParamSpec("P")
R = TypeVar("R")

V = TypeVar("V", bound=Any)
T = TypeVar("T", bound=Any)


class Enum(enum.Enum):
    pass


class Iterable(Protocol[K]):
    """Iterable protocol."""

    def __iter__(self: Iterable[K]) -> Iterator[K]:
        ...


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class User:
    name: str
    age: int


@dataclasses.dataclass(frozen=True)
class Address:
    street: str
    city: str
    state: str


@dataclasses.dataclass(frozen=False)
class Planet:
    name: str
    moons: tuple[str, ...]


@dataclasses.dataclass(order=True, frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str


@dataclasses.dataclass(eq=True, order=True, frozen=True)
class Employee(Person):
    department: str
    salary: float


@dataclasses.dataclass(order=True, frozen=True)
class Card:
    number: int
    issuer: str
    balance: float


# ── Slots ────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotUser:
    name: str
    age: int


# ── Structural Pattern Matching ───────────────────────────────────────────────

def match_pattern(value: T, patterns: list[tuple[Callable[[T], bool], Callable[[T], V]]] | None = None) -> V:
    if not isinstance(patterns, list):
        patterns = [(lambda _: True, lambda x: x)]

    for is_match, transform in patterns:
        if is_match(value):
            return transform(value)


def match_type(obj: object, types: list[type[T]]) -> bool | V | None:
    for t in types:
        if isinstance(obj, t):
            return t()

    return False


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def do_something() -> None:
    print(await asyncio.sleep(random.random()))


async def main():
    await do_something()


# ── Generics ──────────────────────────────────────────────────────────────────

@overload
def get_most_common(items: list[V], k: Literal[0]) -> dict[V, int]: ...
@overload
def get_most_common(items: list[V], k: int) -> list[tuple[V, int]]: ...


def get_most_common(
