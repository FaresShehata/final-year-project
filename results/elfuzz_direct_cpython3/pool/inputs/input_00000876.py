"""
Decorators.
"""

from __future__ import annotations

import functools
import inspect
import itertools as itt
import logging
import numbers
import operator
import sys
import types
import weakref
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field, fields
from datetime import date, datetime, timedelta
from functools import partial
from itertools import chain, filterfalse
from string import Formatter
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
    get_type_hints,
    overload,
)

logger = logging.getLogger(__name__)

try:
    from typing_extensions import Final
except ImportError:
    class Final(type): ...


@dataclass(frozen=True)
class Pair(NamedTuple):
    first : str
    second : str


@dataclass(frozen=True)
class Triple(NamedTuple):
    first : str
    second : str
    third : str


class Adder(Generic[T]):
    def __call__(self, x: T) -> T:
        raise NotImplementedError()


class Multiplier(Generic[T]):
    def __init__(
        self,
        factor: float,
    ) -> None:
        super().__init__()

        self.factor = factor

    def __call__(self, x: T) -> T:
        raise NotImplementedError()


class IntAdder(Adder[int]):
    def __call__(self, x: int) -> int:
        return x + 1


class FloatMultiplier(Multiplier[float]):
    def __call__(self, x: float) -> float:
        return x * self.factor


IntAdder.add = operator.methodcaller("__call__", IntAdder())
FloatMultiplier.mul = operator.attrgetter("factor")


# ── Currying ─────────────────────────────────────────────────────────────────

def curried(func: Callable[..., T]) -> Callable[..., T]:
    """Curries a function by returning a new function with a fixed number of arguments."""

    @functools.wraps(func)
    def _curry(*args: Any, **kwargs: Any) -> Callable[..., T]:
        if not args and not kwargs:
            return func

        @functools.wraps(func)
        def _inner(*more_args: Any, **more_kwargs: Any        all_kwargs = {**kwargs, **keyword_args}
        return func(*all_args, **all_kwargs)

    return decorated_func


add3_1: Callable[[A], Callable[[B], Callable[[C], A]]] = curry_partial(add3)
mul3_1: Callable[[A], Callable[[B], Callable[[C], A]]] = curry_partial(mul3)


assert add3_1(1)(2)(3) == 6
assert mul3_1(1)(2)(3) == 6


# ── Trampoline (finalizer) pattern ────────────────────────────────────────────

def trampoline(fn: Callable[..., T]) -> Callable[..., T]:
    """Trampoline pattern.

    Wraps a potentially recursive function so that it can be called repeatedly
    until it returns a non-recursive value.

    Args:
      fn: Function to wrap.

    Returns:
      Wrapped function which calls fn recursively.

    Example:

      >>> @trampoline
      ... def factorial(n: int) -> int:
      ...     if n <= 1:
      ...         return 1
      ...     else:
      ...         return n * factorial(n - 1)

      >>> factorial(8)
      40320
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwds):
        while True:
            res = fn(*args, **import enum
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
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
