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

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"

@dataclasses.dataclass(slots=True)
class Xyz:
    xyz: tuple[float, float, float]


@dataclasses.dataclass(frozen=True)
class Circle:
    center: Xyz
    radius: float

    def area(self) -> float:
        return math.pi * self.radius**2



# ── Iterators & Generators ────────────────────────────────────────────────────

def fib(n: int) -> Generator[int, None, None]:
    yield 0
    if n > 0:
        yield 1
    last: int = 0
    next: int = 1
    for _ in range(1, n):
        last, next = next, last + next
        yield next


async def fibonacci() -> AsyncGenerator[int, None]:
    yield 0
    if n := await loop.sock_recv(sock, 8):
        yield 1
        yield from asyncio.as_completed((fibonacci(),))


# ── Structural Pattern Matching ───────────────────────────────────────────────

class BrowserType(str, enum.Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


browser_types: set[BrowserType] = {BrowserType.CHROME, BrowserType.FIREFOX}

match browser_types:
    case {BrowserType.CHROME, BrowserType.FIREFOX}: ...
    case _:                                      ...



# ── Walrus Operator ──────────────────────────────────────────────────────────

sum_ = 0
while v := input():
    sum_ += int(v)



# ── Generics ─────────────────────────────────────────────────────────────────

def some_generic_fn(a: T, b: V) -> tuple[T, V]: ...
F = TypeVar("F", bound=Callable[..., Awaitable[Any]])

@overload
def call_aio_fn(fn: F, args: tuple) -> Awaitable[Tuple[T, Tuple]]: ...

@overload
def call_aio_fn(fn: F, args: tuple, kwargs: dict[str, Any]) -> Awaitable[Tuple[T, Dict[str, Any]]]: ...

async def call_aio_fn(fn: F, args: tuple, kwargs: dict[str, Any]=None) -> Tuple[T, Any]:
    if kwargs is None:
        result = await fn(args)
    else:
        result = await fn(*args, **kwargs)
    return result





# ── Asynchronous Programming with Tasks, Futures, Eventloop ───────────────────-

async def aevent_loop():
    tasks = [
        task1(),
        task2(),
        task3()
    ]
    done, pending = await asyncio.wait(tasks)
    for t in done:
        print(t.result())

async def task1() -> str:
    await asyncio.sleep(1)
    return "task1"

async def task2() -> str:
    await asyncio.sleep(1)
    return "task2"

async def task3() -> str:
    await asyncio.sleep(1)
    return "task3"



# ── Asynchronous Programming with Tasks, Futures, Eventloop (cont.) ───────────

async def main():

    tasks = [
        task1(),
        task2(),
        task3()
    ]
    done, pending = await asyncio.wait_for(asyncio.gather(*tasks), timeout=2)
    for t inimport time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


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
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"

sensor = Sensor(label="Humidity", reading=38.7)
assert sensor.label == "Humidity"
assert sensor.reading == 38.7


# ── string.Format ────────────────────────────────────────────────────────────

class Color(NamedTuple):
    r: int
    g: int
    b: int

format_spec = "{color.r}-{color.g}-{color.b}"
template = textwrap.dedent(
"""\
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
      <rect fill="#{:>s}" width="{w}" height="{h}" />
    </svg>
""")
data = template.format(color=Color(r=192, g=192, b=0), w=100, h=100, width=100, height=100)
print(data)


# ── threading ────────────────────────────────────────────────────────────────

start  = time.perf_counter()
threads: list[threading.Thread] = []
for i in range(10):
    thread = threading.Thread(target=lambda: print(i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
end = time.perf_counter()
