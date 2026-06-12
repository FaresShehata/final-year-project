"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          dataclasses (order, frozen, slots), generic container (generic class),
          decorators (type annotations, runtime_checkable, overload, no_type_check),
          protocols (protocols), dataclasses (dataclass), generic container (Generic),
          decorators (type annotations, runtime_checkable, overload, no_type_check).
"""

import enum
from collections import namedtuple
from enum import auto
from functools import wraps
from itertools import count
from operator import attrgetter
from pickletools import long1
from random import choice, randint
from re import subn
from time import sleep
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)
from warnings import warn
from weakref import proxy

from concurrent.futures import Future as CfFuture
from contextlib import suppress, redirect_stdout, AbstractContextManager
from dataclasses import (
    dataclass,
    field,
    fields,
    is_dataclass,
    InitVar,
    MISSING,
    _MISSING_TYPE,
    fields_from_enum,
    _FIELD_DEFAULTS,
    _field_cannot_be_assigned,
)


def counter() -> Iterator[int]:
    for i in count():
        yield i


# ── Runtime checkable ─────────────────────────────────────────────────────────

T = TypeVar("T")


def runtime_checkable(type_: type[T]) -> type[T]:
    """Copied from typing_extensions.runtime_checkable."""
    class FakeClass:

        pass

    setattr(FakeClass, "__origin__", type_)

    class MyRuntimeCheckableMeta(type):

        def __instancecheck__(cls, instance):
            try:
                type(instance).__origin__
            except AttributeError:
                return False
            else:
                return super().__instancecheck__(instance)

    return MyRuntimeCheckableMeta(f"{FakeClass.__qualname__}Wrapper", (object,), {"__annotations__": {}})


# ── Decorators ─────────────────────────────────────────────────────────────────

def no_type_check(func: Callable[..., T]) -> Callable[..., T]:
    """Copied from typing_extensions.no_type_check."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with suppress(TypeError):
            result = func(*args, **kwargs)
        return result
    return wrapper


def runtime_checkable_with_over

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


class PriorityQueue(Generic[K, V]):
    """
