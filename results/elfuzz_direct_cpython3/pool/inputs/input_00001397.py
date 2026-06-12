"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import functools
import hashlib
import json
import math
import random
import re
import sqlite3
import time
import types
import urllib.request
import warnings
from collections.abc import Callable, Iterable
from contextlib import suppress
from datetime import date, datetime, timedelta
from email.utils import formatdate as email_format_date
from itertools import chain, groupby, islice, repeat
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    ClassVar,
    Collection,
    Container,
    Generic,
    Literal,
    Optional,
    Sequence,
    TypeAlias,
    TypedDict,
)

# https://stackoverflow.com/a/67981574
if False:  # pragma: no cover
    from ._mypy_extensions import (
        Attrs,
        AsyncContextManagerT,
        EnvT,
        GenericT,
        LazyT,
        MetaClassT,
        OverloadedT,
        PydanticModelT,
        RuntimeAttrsT,
    )

    _MYPY = True


@dataclasses.dataclass(frozen=True)
class Dataclass:
    name: str


Dataclass.name


@dataclasses.dataclass(slots=True)
class SlotsDataclass:
    name: str


SlotsDataclass.name


@dataclasses.dataclass(order=True)
class OrderedDictDataclass:
    a: int
    b: str


OrderedDictDataclass(1, "a")


@dataclasses.dataclass(eq=False)
class NoEqualityDataclass:
    a: int


NoEqualityDataclass(1)


@functools.lru_cache(maxsize=None)
def expensive_function():
    return 1 + 2 * 3 - 4 // 5 * 6 % 7


expensive_function()


class PositiveInteger(int):
    def __new__(cls, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Value must be a positive integer.")
        return super().__new__(cls, value)

    @classmethod
    def validate(cls, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(
                f"{value} is not an instance of {cls.__name__}."
                " Value must be a non-negative integer."
            )


PositiveInteger.validate(-1)


@enum.unique
class Color(enum.Enum):
    RED = enum.auto()
    BLUE = enum.auto()
    GREEN = enum