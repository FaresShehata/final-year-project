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
import time
import types
import warnings
from abc import ABCMeta
from collections import (
    ChainMap,
    Counter,
    deque,
    OrderedDict,
    namedtuple,
    UserDict,
    UserList,
    UserString,
)
from concurrent.futures import Future as ConcurrentFuture
from contextlib import suppress
from functools import cached_property, partialmethod, reduce
from inspect import Parameter, Signature, signature
from itertools import chain, count, cycle
from pathlib import Path
from pprint import pprint
from string import ascii_letters, digits, punctuation
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Generator,
    Generic,
    Hashable,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    NoReturn,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeAlias,
    TypeGuard,
    Union,
    get_args,
    get_origin,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    from _typeshed import SupportsLessThan

    PassThruType = TypeVar("PassThruType")
else:

    class PassThruType(type):
        pass

# noinspection PyShadowingBuiltins
class NotDefined(enum.Enum):  # pragma: nocover
    """Used for sentinel values that are not defined yet."""

    def __repr__(self) -> str:
        return self.__name__

    def __str__(self) -> str:
        return self.name


IntEnum = type(NotDefined)  #: A convenience alias for the built-in :py:class:`enum.Enum`.

IOTypes = TypeVar("IOTypes")  #: A type variable representing I/O types.
FSPathLikeTypes = TypeVar(
    "FSPathLikeTypes"
)  #: A type variable representing file system path-like objects.

IOTypesAndPaths = Union[IOTypes, FSPathLikeTypes]
"""Union of ``IOTypes`` and ``FSPathLikeTypes``."""

AsyncCallable = Callable[..., Awaitable]
"""A callable that returns an awaitable."""

AnyStr = Union[str, bytes]
"""A union of ``str`` and ``bytes``."""

Awaitable = Coroutine[Any, Any, Any]
Coroutine = Callable[
    [Parameter.empty * P_],
    Awaitable[Any],
]
"""A coroutine callable (i.e. a function declared with ``async def``)."""


class AsyncIterator(G    "prefixes_and_suffixes",
    "random_password_string",
    "reversed_sequence",
    "timeout_decorator",
    "typed_dict_from_callable",
]

P_ = ParamSpec("P_")

NoneOrT = TypeVar("NoneOrT", None, TypeVar("T"))
"""A union of `None` and any type."""

IterableOfT = TypeVar("IterableOfT")
"An iterable of a type `T`."

NonEmptyIterableOfT = TypeVar("NonEmptyIterableOfT")
"""An iterable of length at least one."""

ReversibleSequenceOfT = TypeVar("ReversibleSequenceOfT")
"""A reversible sequence of a type `T`. This includes lists, tuples, strings, etc."""


def any(*values: bool) -> bool:
    """Return True if any argument evaluates to True."""
    return any(values)


@overload
def counter(iterable: None = ..., start: int = ...) -> Counter[int]:
    ...


@overload
def counter(iterable: Iterable[T], /, *, start: T = ...) -> Counter[T]:
    ...


def counter(
    iterable: Iterable[T] | None = ...,
    *,
    start: T = ...,
) -> Counter[Hashable] | Counter[T]:
    """
    Return a new Counter object, optionally initialized from an iterable.

    >>> c = counter([1, 2, 3])
    >>> print(c)
    Counter({1: 1, 2: 1, 3: 1})
    >>> c = counter(start='a')
    >>> print(c['a'])
    1
    """
    if isinstance(iterable, dict):
        return collections.Counter(iterable, **locals())
    elif not iterable:
        return collections.Counter(**locals())
    else:
        return collections.Counter(iterable, **locals())


def default_dict_factory() -> defaultdict:
    """Default factory function used when creating new dictionaries in defaultdict()."""
    return defaultdict(default_dict_factory())


def enumerate(obj: Iterable[Any]) -> Enumerator[Any]:
    """
