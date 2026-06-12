"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
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
        if self.attrname in obj.__dict__:
            return obj.__dict__[self.attrname]
        val = self.func(obj)
        if val is NotImplemented:
            return getattr(obj.__class__, self.attrname, None)
        return val


# ── Abstract base classes ─────────────────────────────────────────────────────

class BaseABC(metaclass=abc.ABCMeta):
    pass


class A(BaseABC):
    ...


class B(A):
    ...


def abstractmethod(funcobj: Callable[..., T]) -> Callable[..., T]:
    """
    Function decorator for declaring abstract methods.
    """
    return funcobj


# ── Decorators ────────────────────────────────────────────────────────────────

def classproperty(func):
    """
    Class decorator which converts a method into a class attribute.

    >>> class C(object):
    ...     @classproperty
    ...     def foo(cls): return 'bar'
    ...
    >>> c = C()
    >>> c.foo
    'bar'

    """

    attr_name = "_{}_{}".format(func.__name__, id(func))
    @functools.wraps(func)
    def wrapper(self=None):  # pylint: disable=unused-argument
        return func()

    setattr(wrapper, "__isabstractmethod__", True)
    setattr(C, attr_name, wrapper)
    return property(wrapper)


# ── Context-managers ─────────────────────────────────────────────────────────

class ContextManagerTest:
    def __enter__(self):
        print("Entered context manager")
        return "Context Manager Test"

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exited context manager")


class ContextDecoratorTest:
    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            with ContextManagerTest() as cm_test:
                result = func(cm_test, *args, **kwargs)
            return result

        return wrapped


@contextlib.contextmanager
def nested_context_manager():
    print("Entering nested context manager")
    try:
        yield None
    finally:
        print("Exiting nested context manager")


@contextlib.contextmanager
def inner_context_manager():
    print("Entering inner context manager")
    try:
        yield None
    finally:
        print("Exiting inner context manager")


@contextlib.contextmanager

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


# ── Async machinery ───────────────────────────────────────────────────────────

