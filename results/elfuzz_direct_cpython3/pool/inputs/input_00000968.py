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
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from typing_extensions import Protocol


def seed():
    random.seed(42)


T = TypeVar("T")
K = TypeVar("K", contravariant=True)
V = TypeVar("V")


# https://docs.python.org/3/library/typing.html#protocols
class Protocol(Protocol):
    pass


@dataclasses.dataclass(frozen=True)
class Node:
    value: int
    left: Optional[Node] = None
    right: Optional[Node] = None


async def foo() -> None:
    print("foo")


class Foo:
    @classmethod
    async def bar(cls) -> None:
        print("bar")
        await foo()


print(Node.__annotations__)


# >>> {'value': <class 'int'>}
class A:
    a: str


b: A = A()
print(b.a)
# >>> AttributeError: 'A' object has no attribute 'a'

# >>> TypeError: 'str' object is not callable
# b()

# >>> SyntaxError: identifier starts with '__'
# class __B:
#     ...

class B:
    __a: str


c: B = B()
print(c._B__a)
# >>> AttributeError: 'B' object has no attribute '_B__a'


class C:
    _d: str


print(C._C__d)
# >>> AttributeError: type object 'C' has no attribute '_C__d'

# >>> SyntaxError: invalid syntax
# class D:
#     __e: str
#     _f: str


class E:
    e: str


# >>> Invalid escape sequence: '\_'
# class F:
#     f: str

# >>> UnboundLocalError: local variable 'g' referenced before assignment
# class G:
#     g = "hello"
#     g += "world"


class H:
    h = ("h", "e", "l", "l", "o")
    # >>> AttributeError: 'H' object has no attribute 'i'
    # i = h


class I:
    i = {"a": "b"}
    # >>> KeyError: 'key'
    # i["key"]


class J:
    j = {1, 2, 3}
    # >>> IndexError: list index out of range
    # j[0]


class K:
    k = [1, 2, 3]
    # >>> IndexError: list index out of range
    # k[0]

# >>> AttributeError: module 'dataclasses' has no attribute 'field'
# class L(dataclasses.field):
#     l = Field(default=str)


# >>> TypeError: unhashable type: 'list'
# class M(list):
#     m = M([1, 2, 3])

# >>> TypeError: unhashable type: 'set'
# class N(set):
#     n = N((1, 2, 3))

# >>> TypeError: unhashable type: 'tuple'
# class O(tuple):
#     o = O((1, 2, 3