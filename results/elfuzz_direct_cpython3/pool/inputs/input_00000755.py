"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining, etc.
"""

import asyncio
from contextlib import asynccontextmanager
import re
import sys
import os
import pathlib
import timeit
from types import TracebackType
from typing import Any, AsyncGenerator, Generator, Optional, cast, overload

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")  # noqa: E402
from typing_extensions import Self, override

import numpy as np

from src import ROOT_PATH, printme
from src.infrastructure.asyncio_awaitables import _async_test_func, _yielder
from src.utils.decorators import memoize
from src.utils.exceptions import CustomException
from src.utils.misc import (
    BaseClass,
    ComposedBaseClass,
    deprecate,
    deprecated_method,
    has_attr,
    has_property,
    is_abstract,
    is_classmethod,
    is_method,
    is_staticmethod,
    make_immutable,
    set_attribute,
)
from src.utils.typing import (
    AsyncIterable,
    AsyncIterator,
    BaseAsyncContextManager,
    ContextManager,
    Coroutine,
    Dict,
    IO,
    IOStream,
    Iterator,
    List,
    LiteralString,
    NewType,
    Optional,
    Set,
    Tuple,
    TypedDict,
    Union,
    ValuesView,
    cast,
    get_origin,
)


"""
Bootcamp 14 — Python functions, decorators, decorators with parameters, lambdas,
              default arguments, keyword-only arguments, positional-only arguments,
    <|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>          walrus operator, typing generics, exception groups, ExceptionGroup
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
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised for IDEs

from abc import abstractmethod, abstractstaticmethod
from collections.abc import (
    Container,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
)
from contextlib import suppress
from functools import partial, reduce
from itertools import chain, count, cycle, islice, product, repeat, takewhile
from logging import Logger
from math import ceil, log, floor, gcd as _gcd, sqrt, pow

# ── typing types ─────────────────────────────────────────────────────────────

KT = TypeVar("KT")
VT = TypeVar("VT", bound="V")

T = TypeVar('T')
class TArgs(Generic[T]):
    ...

UnionTypeVars = Union[*T]

# ── builtins types ───────────────────────────────────────────────────────────


def _merge(*iterables: Iterable[T], key: Callable[[T], float]) -> list[T]:
    heap: list[tuple[float, T]] = []
    for iterable in iterables:
        iterator = iter(iterable)
        try:
            first = next(iterator)
            heap.append((key(first), first,))
        except StopIteration:
            continue
    while len(heap) > 0:
        _, value = heapq.heappop(heap)
        yield value
        try:
            item = next(value)
            heapq.heappush(heap, (key(item), item,))
        except StopIteration:
            continue


@overload
def merge(*iterables: Iterable[T], key: None = ...) -> list[T]: ...
@overload
def merge(*iterables: Iterable[T], key: Callable[[T], float]) -> list[T]: ...
def merge(*iterables, key=None):  # type: ignore[no-untyped-def]
    """
    Merge multiple sorted lists into a single sorted output.
    >>> [3, 6, 8, ..., 69]
    """
    assert all(isinstance(i, Iterable) and isinstance(next(iter(i)), T) for i in iterables), \
           "All arguments must be iterables"
    if not any(key is not None for key in map(None, *iterables)):
        return list(chain.from_iterable(iterables))

    # Use the first element of each iterable to decide which one to consume next
    iterators = iter(i) for i in iterables
    keys = (_next_key(it) for it in iterators)
    heap = [(k, v) for k, v in        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
