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
import random
import re
import timeit
import weakref
from collections import defaultdict
from datetime import timedelta
from hashlib import sha1
from inspect import iscoroutinefunction
from itertools import chain, groupby, product
from math import floor
from pathlib import Path
from string import ascii_lowercase as alphabet
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeGuard,
    TypedDict,
    Union,
)

# -------------------------------------------------------------------------------------------------

def seedit(seed: int = None) -> int:
    if seed is not None:
        random.seed(seed)
    return random.randint(0, 99_999)


def random_item(iterable: Iterable[Any]) -> Any:
    return iterable[floor(random.random() * len(iterable))]


def random_choice(sequence: Sequence[Any], /) -> Any:
    return sequence[random.randrange(len(sequence))]


def random_sample(population: Sequence[Any], k: int = 1) -> list[Any]:
    """Return a list of k unique elements chosen from the population."""
    # TODO: use `random.sample` instead?
    result: list[Any] = []
    while True:
        item = random.choice(population)
        if item in result:
            continue
        result.append(item)
        if len(result) == k:
            break
    return result


def random_index(lst: List[Union[int, float]]) -> int:
    return floor(random.random() * len(lst))


class RandomSequence(Generic[T]):
    def __init__(self, lst: List[T], *, seed: int = None):
        self._lst = lst
        self._idx = -1
        self._seed = seed or seedit()

    def _next(self, default=None):
        try:
            idx = self._idx + 1
            self._idx += 1
            return self._lst[idx]
        except IndexError:
            self._idx = -1
            return default

    def next(self) -> T:
        return self._next(default=stop())

    @property
    def index(self) -> int:
        return self._idx


def option(x: Any) -> Option:
    return Some(x) if x else None


Stopper = Callable[[Any], bool]


def stop(*args: Any, **kwds: