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


__all__ = [
    'Any',
    'Awaitable',
    'Callable',
    'ClassVar',
    'Coroutine',
    'DispatchKey',
    'EnumMember',
    'GenericMeta',
    'Hashable',
    'Iterator',
    'Literal',
    'Optional',
    'Protocol',
    'RecursiveList',
    'Sequence',
    'Self',
    'T',
    'TypedDict',
    'Union',
]

DispatchKey = int
T = TypeVar('T')
S = TypeVar('S')

SecondArgType = TypeVar('SecondArgType', bound=Callable[..., Any])
ThirdArgType = TypeVar('ThirdArgType', bound=Callable[..., Any])

LambdaReturnType = TypeVar('LambdaReturnType', bound=lambda *a, **kw: Any)
FirstReturnType = TypeVar('FirstReturnType', bound=lambda x: Any)

LazyType = TypeVar('LazyType', bound='Lazy[object]')

self_type = TypeVar('self_type')


class Self(S):
    pass


@dataclasses.dataclass(frozen=True)
class MetaData:
    """Metadata about a function."""

    is_async: bool = False
    is_coroutine: bool = False
    is_generator: bool = False
    __name__: str


AnyFunc = Callable[..., Any]
AnyCallable = Callable[..., Any]
AnyIterable = Iterable[Any]


class Lazy(Generic[T]):
    """
    A lazy object that evaluates its value only when it's needed.
    """

    def __init__(self, func: Callable[[int], T]) -> None:
        self._func = func

    def __call__(self, n: int) -> T:
        return self.get(n)

    def get(self, n: int) -> T:
        return self._func(n)

    __repr__ = repr
    __str__ = str


@typing.overload
def cache(
    f: Callable[..., T],
    *,
    maxsize: int | float | None = ...,
    typed: bool = ...,
    key: Callable[..., DispatchKey] | None = ...,
) -> Callable[..., T]:
    ...


@typing.overload
def cache(
    *,
    maxsize: int | float | None = ...,
    typed: bool = ...,
    key: Callable[..., DispatchKey] | None = ...,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    ...


def cache(  # type: ignore[misc]
    f=None    FirstReturnType,
    LambdaReturnType,
    LazyType,
    SecondArgType,
    ThirdArgType,
    ThreadingExecutorType,
    ThreadPoolExecutorType,
    WrappedFunctionType,
)


# @classmethod decorator
def classmethod_decorator(func: Callable = None, *, name: