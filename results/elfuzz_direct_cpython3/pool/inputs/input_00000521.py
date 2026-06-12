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
import pathlib
import random
import sys
import textwrap
import types
import typing as t
from abc import ABCMeta
from copy import deepcopy
from datetime import timedelta
from functools import partial
from itertools import chain
from math import sin
from typing import Any, Callable, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union

import aioredis
import attrs
import humanize
import more_itertools as mi
import orjson
from attrs import define, field
from attrs.converters import optional
from attrs.validators import instance_of
from attrs_mate import AttrsMateMixin
from hypothesis.strategies import SearchStrategy
from loguru import logger
from more_itertools.more import first_true
from pydantic import BaseModel
from pydantic.generics import GenericModel
from pydantic.types import JSONType
from pydantic.utils import deep_update

from .core import (
    DEFAULT_LOGGING_LEVEL,
    DEFAULT_LOGGING_FORMAT,
    DEFAULT_LOGGING_HANDLER,
    DEFAULT_LOGGING_FILE_NAME,
    LogConfig,
    Logger,
    LogLevel,
    LoggingHandler,
    LoggingFormatter,
    LoggingFileBackend,
    LoggingFileHandler,
    setup_logging,
)
from .utils import get_caller_info

# ── Typing aliases ────────────────────────────────────────────────────────────


# ── Dataclasses ───────────────────────────────────────────────────────────────


@attrs.define(
    kw_only=True,
    weakref_slot=False,
    frozen=True,
)
class Person:
    name = "Jane Doe"
    age = 30
    is_bald = False


@define(kw_only=True, frozen=True)
class Person:
    name: str = "Jane Doe"
    age: int = 30
    is_bald: bool = False


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def from_array(cls, array: list[float]):
        return cls(*array)

    def to_json(self):
        return {
            'x': self.x,
            'y': self.y,
        }


def _get_person() -> Person:
    return Person()


person = _get_person()

print(person.name)


@dataclass(frozen=True)
class Point:
    x: float = 1.5708
    y: float = 1.4142


p = Point()
assert p.x == p.y == 1.5708 + 1.4142


# ── Structural Pattern Matching ────────────────────────────────────────────────


async def generate_users():
    for i in range(10):
        yield User(name=f'user-{i}', age=random.randint(10, 60))


users: list[User] = []
for user in await generate_users():
    users.append(user)


def find_user_by_age(users: list[User], age: int) -> Optional[User]:
    for user in users:
        if user.age == age:
            return user

    return None


def find_user_by_age_ternary(users: list[User], age: int) -> Optional[User]:
    return next(filter(lambda u: u.age == age, users), None)


def find_user_by_age_struct_pattern(users: list[User], age: int) -> Optional[User]:
    return next((user for user in users if user.age == age), None)


assert find_user_by_age(users, 35) == find_user_by_age_ternary(users, 35)
assert find_user