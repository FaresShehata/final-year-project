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
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5


@dataclasses.dataclass(order=True, frozen=True, slots=True)
class Circle(Point):
    radius: float

    @property
    def area(self) -> float:
        return 3.14 * self.radius ** 2


# ── Slots ─────────────────────────────────────────────────────────────────────

# class Point:
#     __slots__ = ["x", "y"]

#     def __init__(self, x: float, y: float) -> None:
#         self.x = x
#         self.y = y


# class Circle(Point):
#     def __init__(self, center: Point, radius: float) -> None:
#         super().__init__(center.x, center.y)
#         self.radius = radius


# circle = Circle(Point(0, 0), 7)


# ── Structural Pattern Matching ───────────────────────────────────────────────

@overload
def move(value: int) -> None: ...
@overload
def move(value: float) -> None: ...
@overload
def move(value: str) -> None: ...
def move(value: V) -> None:
    if isinstance(value, int):
        print(f"Value of type int: {value}")
    elif isinstance(value, float):
        print(f"Value of type float: {value}")
    else:
        print("Value was a string")


move(1)
move(1.0)
move("Hello World")


# ── Walrus Operator ───────────────────────────────────────────────────────────

points: list[Point] = [Circle(0, 0), Circle(1, 1)]

for point in points:
    if (d := point.distance_to_origin()) < 1:
        print(d)


# ── Typing Generics ───────────────────────────────────────────────────────────

class MyList(list[T]):
    def append(self, item: T) -> None: ...
    def extend(self, iterable: Iterable[T]) -> None: ...
    def insert(self, index: int, value: T) -> None: ...
    def remove(self, value: T) -> None: ...
    def pop(self, index: int = -1) -> T: ...

l = MyList([1])
(l).append(2)
print(len(l))


# ── Exception Groups ──────────────────────────────────────────────────────────

raise ExceptionGroup(
    "Multiple errors",
    [
        RuntimeError("Something went wrong"),
        ZeroDivisionError(),
        TypeError("The second argument must be an integer"),
    ]
)


# ── Custom exception group with custom `exception_message` method ─────────────

class RaiseExceptionGroup(ExceptionGroup):
    def exception_message(self) -> str:
        return "\n".join(str(e) for e in self.exceptions)

raise RaiseExceptionGroup(
    "Multiple errors",
    exceptions=[
        RuntimeError("Something went wrong"),
        ZeroDivisionError(),
        TypeError("The second argument must be an integer"),
    ],
)


# ── Custom exception group with a single inner exception ──────────────────────

class SingleInnerExceptionGroup(ExceptionGroup):
    def exception_message(self) -> str:
        return str(next(iter(self.exceptions)))

raise SingleInnerExceptionGroup(
    "Single error",
    exceptions=RuntimeError("Something went wrong"),
)

# ── TODO ──────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────

"""
asyncio.run(asyncio.sleep(1))

with open("/etc/passwd") as file:
    print(file.read())

deque(maxlen=5)[1]

bisect.bisect_left(range(10), 9)

Counter({"a": 1, "b": 2})

random.random()

re.search(r"\w+", "hello world").group(0)
"""


# ─────────────────────────────────────────────────────────────────────────────

"""
list(map(lambda x: x**2, range(10)))
list(filter(lambda x: x%2 == 0, range(10)))

sorted(dataclasses.asdict(point))
sorted(Circle(0, 0).area)
sorted(circle.area)

heapq.nlargest(3, [1, 8, 5, 3, 9, 6])

next(filter(None, [None, True]))
next((v for v in [1, 2, 3] if v % 2 == 0), 0)

it = iter(range(10))
next(it)
"""



# ─────────────────────────────────────────────── ‾‾‾‾ ‾‾‾‾ ‾‾‾‾ ‾‾‾‾ ‾_T = TypeVar('_T')

@runtime_checkable
class _Iterable(TypedDict):
    __mro_entries__: tuple[type[_T], ...]


@runtime_checkable

# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
