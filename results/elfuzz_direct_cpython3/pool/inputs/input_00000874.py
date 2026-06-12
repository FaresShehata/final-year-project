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
        self.cache = WeakKeyDictionary()


class WeakKeyDictionary(dict):
    """
    Dictionary that doesn't prevent the keys from being garbage-collected.

    >>> class A:
    ...     d = WeakKeyDictionary()
    ...
    >>> a1 = A()
    >>> a2 = A()
    >>> a1.d[a1]
    {}
    >>> a1.d[a2]
    {}

    The values are also weak-referenced:

    >>> a3 = A()
    >>> a1.d[a3]
    {}
    del a3
    >>> a1.d[a3]
    Traceback (most recent call last):
      ...
    KeyError: a3

    And can be iterated over:

    >>> for i in a1.d:
    ...     print(i)
    <object at 0x7f96bfaa48d0>
    <object at 0x7f96c0ea4e10>

    """

    def __missing__(self, key):
        self[key] = value = defaultdict(list)
        return value

    def __delitem__(self, key):
        super().__delitem__(key)
        for value in self.values():
            try:
                value.pop(key)
            except KeyError:
                continue

    def clear(self):
        while True:
            try:
                key = next(iter(self))
            except StopIteration:
                break
            else:
                del self[key]


class Meta(type):
    def __new__(metacls, classname, supers, classdict):
        cls = super(metaclass=metacls). \
              __new__(metacls, classname, supers, classdict)

        if "__slots__" in classdict and '__dict__' not in classdict["__slots__"]:
            classdict["__slots__"].append("__dict__")

        cls.__metaclass__ = metacls

        return cls

    def __call__(cls, *args, **kwargs):
        instance = super(metaclass=cls.__metaclass__, type=cls).__call__(*args, **kwargs)
        instance.__dict__["__weakref__"] = weakref.ref(instance)
        return instance


class SingletonMeta(type):
    instances: ClassVar[WeakKeyDictionary] = WeakKeyDictionary()

    def __call__(cls, *args, **kwargs):
        inst = super(SingletonMeta, cls).__call__(*args, **kwargs)
        cls.instances[inst] = inst
        returnK = TypeVar("K")
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
            "priority": self.priority.value,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(**{**data, "priority": Priority(data["priority"]), "status": Status(data["status"])})


# ── Slots ─────────────────────────────────────────────────────────────────────

class ExampleClass:
    __slots__ = ["_value"]

    def __init__(self):
        self._value = ""

    def set_value(self, value: str) -> None:
        self._value = value

    def get_value(self) -> str:
        return self._value


# ── Structural pattern matching ───────────────────────────────────────────────

def match_obj(obj: V) -> K:
    match obj:
        case str():
            return obj.upper()

        case list() as items:
            return items[-1].upper()

        case _: raise ValueError(f"Unexpected value: {obj!r}")

    # unreachable code
    assert False, "Unreachable"


def match_list(lst: list[V]) -> K:
    match lst:
        case []:
            return []

        case [first, second]:
            return first + second

        case [head] | [head, tail] | [*rest]:
            return head

        case [] | [_]: raise ValueError("Expected at least one item")

    # unreachable code
    assert False, "Unreachable"

