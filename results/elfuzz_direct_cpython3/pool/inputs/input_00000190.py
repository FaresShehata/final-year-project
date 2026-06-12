"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""
from __future__ import annotations

import asyncio
import contextvars
import enum
import types
import warnings
from collections.abc import AsyncIterable, Awaitable, Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import MissingFieldError, dataclass, field, fields
from functools import partial, wraps
from typing import (
    Any,
    ClassVar as _ClassVar,
    Generic,
    Literal,
    NewType,
    NoReturn,
    Optional,
    ParamSpec,
    Protocol,
    TypeAlias,
    TypedDict,
    TypeGuard,
    Union,
)

from .compat import is_async_function


P = ParamSpec("P")
T = TypeVar("T")


def f(x: int) -> int:
    return x + 1


f(5)


@dataclass(frozen=True)
class A:
    b: str = "b"


a = A()


A.b
# 'b'

A()
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# TypeError: __init__() takes 1 positional argument but 2 were given


A(b=7).b
# 7


async def g() -> None:
    a_ = A(a="a")
    print(a_.a)
    print(a.a)
    assert a == a_
    assert a != a_


g()
# a
# b
# True
# False


@dataclass(frozen=True)
class B:
    c: float = 3.141592653589793


B.c
# 3.141592653589793

B(c=4.4).c
# 4.4

B().c
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# AttributeError: '_FrozenInstanceData' object has no attribute 'c'


@dataclass(slots=True, frozen=True)
class C:
    d: bool = True


C.d
# True

C(d=False).d
# False

C().d
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# AttributeError: '_FrozenInstanceData' object has no attribute 'd'

warnings.warn(
    "\n\nThe `slots` option