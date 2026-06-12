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
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 9


class Theme(enum.StrEnum):
    LIGHT  = "light"
    DARK   = "dark"


@runtime_checkable
class Message(Protocol[K]):
    message_id: K

    def to_dict(self) -> dict[str, Any]:
        ...

    def from_dict(self, d: dict[str, Any]) -> Self:
        ...


# ── Dataclasses ───────────────────────────────────────────────────────────────
dataclasses.dataclass
dataclasses.field
dataclasses.replace
dataclasses.astuple
dataclasses.asdict


@dataclasses.dataclass(init=False, frozen=True)
class Person():
    first_name: str
    last_name: str

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ── Slots ────────────────────────────────────────────────────────────────────
__slots__ = ["x", "y"]
_=object
class Point(_):
    x: int
    y: int
    z: int = 2


# ── Structural Pattern Matching ──────────────────────────────────────────────

_=Pattern
_=match
_=case
_=_=


# ── Walrus Operator ──────────────────────────────────────────────────────────
a := b
c += d
e -= f


# ── Generics ─────────────────────────────────────────────────────────────────
TypeVar
Generic[T]
re.sub(r"\b[a-z]+\b", lambda m: m.group().upper(), string)


# ── Async ───────────────────────────────────────────────────────────────────-

async def sleep(n: int | float) -> None:
    await asyncio.sleep(n)


async def coroutine_with_yield_from() -> int:
    yield from range(10)
    return sum(range(10))

coroutine_with_yield_from()


# ── Exceptions ───────────────────────────────────────────────────────────────

try:
    ...
except ZeroDivisionError as e:
    print(e.__str__())  # repr()
    print(repr(e))      # str()
    print(e.args)       # tuple(args)
except (TypeError, RuntimeError) as e:
    print(type(e))
else:
    print("no error")


class MyException(Exception):
    def __init__(self, *args: object) -> None:
        pass


ex: MyException = MyException()
print(ex.args        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


class Circle(Shape):
