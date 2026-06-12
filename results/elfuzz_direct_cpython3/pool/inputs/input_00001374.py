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


class Color(enum.Flag):
    RED     = enum.auto()
    GREEN   = enum.auto()
    BLUE    = enum.auto()
    YELLOW  = enum.auto()

    @property
    def rgb(self) -> str:
        return "".join(sorted(map(str, self)))  # sorted by default (not guaranteed to be stable sort)


# ── Async/Await ───────────────────────────────────────────────────────────────

class Task(Generic[K]):
    _id_counter: ClassVar[int] = 0
    _tasks: ClassVar[list[Task]] = []

    id: int
    func: Callable[..., K]
    args: tuple
    kwargs: dict[str, object]

    def __init__(
            self,
            func: Callable[..., K],
            *args: object,
            **kwargs: object
    ) -> None:
        super().__init__()
        self.id = Task._id_counter + 1
        self.func = func
        self.args = args
        self.kwargs = kwargs
        Task._tasks.append(self)

    @classmethod
    def get_all(cls) -> list[Task]:
        return cls._tasks[:]


async def task(func: Callable[..., K], *args: object, **kwargs: object) -> K:
    return await asyncio.get_running_loop().run_in_executor(None, lambda *a, **k: func(*a, **k))


async def do_it() -> None:
    tasks = [
        task(
            lambda x: x*x,
            *[random.randint(1, 10)**2 for _ in range(3)],
        ),
        *[
            task(lambda a, b: a+b, arg1, arg2)
            for arg1, arg2 in zip([1, 2], [3, 4])
        ],
        task(lambda c: c*c, *(int(i) for i in ["1", 2])),
        task(
            lambda d, *e, f: d*d+sum(e)+f*f+f**d,
            9, *[random.randint(1, 10) for _ in range(3)], -2
        )
    ]

    results = await asyncio.gather(*tasks)
    for res in results:
        print(res)


start_time = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(do_it())
end_time = time.time()
elapsed_time = end_time - start_time
print(f"This#         super().__init__(center.x, center.y)
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
        print(f"Value of type string: {value}")

move(100)  # Value of type int: 100
move(8.6)  # Value of type float: 8.6
move("hi!")  # Value of type string: hi!


class Point:
    def __init__(self, x: int | float, y: int | float) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"(x={self.x},y={self.y})"


# p = Point(x=1.2, y=-3.4)
# if not isinstance(p, Point): raise TypeError
p = Point(x=random.random(), y=random.random())
match p:
    case Point(x, y) as point if (point.x > 0 or point.y > 0) \
                and abs(point.x) == abs(point.y):  # noqa: E721
        print(f"\nPoint ({point}):\n\tThe point is on the line y=x.")
    case Point(x, y) as point if (point.x >= 0 or point.y >= 0) \
                and point.x != point.y:  # noqa: E721
        print(f"\nPoint ({point}):\n\tx is greater than y (or vice versa).")
    case Point(x, y) as point if point.x <= point.y:  # noqa: E721
        print(f"\nPoint ({point}):\n\tThe point is below (or coincides with) the line y=x.")


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False)
class Person:
    name: str
    age: int
    height: float
    weight: float

    @property
    def weight_kg(self) -> float:
        return self.weight * 0.45359237

    @weight.setter
    def weight(self, new_weight: float) -> None:
        self.weight = new_weight

    @staticmethod
    def from_json(json_str: str) -> Person:
        d = json.loads(json_str)
        return Person(**d)

    @classmethod
    def from_csv(cls, csv_str: str) -> Person:
        fields = re.split(r',|;', csv_str)
        try:
            return cls(*(fields[i    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

