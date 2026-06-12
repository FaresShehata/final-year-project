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
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)


if TYPE_CHECKING:
    ...


T = TypeVar("T")
U = TypeVar("U")


def test() -> None:
    assert True


test()


# ── Enums ─────────────────────────────────────────────────────────────────────

# ── Base classes ─────────────────────────────────────────────────────────────-

@dataclasses.dataclass(frozen=True)
class Task:
    """
    A task to be performed.
    """

    id: int
    name: str
    priority: Priority
    status: Status
    tags: List[str]


@enum.unique
class Priority(enum.Enum):
    """Priorities of tasks."""

    NORMAL = 0
    HIGH = 1


@enum.unique
class Status(enum.IntEnum):
    """Statuses of tasks."""

    NEW = 0
    IN_PROGRESS = 1
    COMPLETED = 2


# ── Derived types ──────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True, kw_only=False, eq=False, unsafe_hash=True)
class TaskWithNewField(Task):
    new_field: int


class TaskList(list[Task]):
    pass


# ── Data Classes and other decorators ──────────────────────────────────────────


# TODO: https://www.python.org/dev/peps/pep-0614/
#       Add `__slots__` and `typing.Generic`?
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>
if TYPE_CHECKING:
    from collections.abc import Mapping


class BaseEnum(Enum):
    """Base class for all enums.

    Provides a context manager that sets the current enum value on enter.
    """

    def __enter__(self) -> Enum:
        old_enum_value = cast(Optional[int], getattr(sys, "__enum_values"))
        setattr(sys, "__enum_values", {**sys.__enum_values, self.name: self.value})
        return self

    def __exit__(self, *exc_info: Any) -> None:
        setattr(sys, "__enum_values", old_enum_value)


@unique
class Priority(BaseEnum):
    LOW = auto()
    NORMAL = auto()  # default
    HIGH = auto()


class AccountType(enum.Enum):
    PERSONAL = "personal"
    BUSINESS = "business"

    @property
    def is_personal(self) -> bool:
        return self == AccountType.PERSONAL

    @property
    def is_business(self) -> bool:
        return not self.is_personal


def identity(x: Any) -> Any:
    return x


def validate_id(value: Any) -> None:
    try:
        UUID(str(value))
    except ValueError:
        raise validators.ValidationError(f"Invalid ID: {value}")


@attr.s(auto_attribs=True, slots=True, frozen=True, kw_only=False)
class Person:
    first_name: str
    last_name: str
    age: int

    @first_name.validator
    def check_first_name(self, attribute: attr.Attribute[str], value: str) -> None:
        if len(value) > 25:
            raise validators.ValidationError("First name too long")


@attrs.define(slots=True, frozen=True, repr=False)
class Dog:
    _name: str
    owner: Person

    @staticmethod
    def make_new(name: str) -> Dog:
        dog = Dog(name=name, owner=None)
        dog.owner = Person(first_name="John", last_name="Doe", age=30)
        return dog

    def bark(self) -> None:
        print(f"{self.name} barks!")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value:
            raise validators.ValidationError("Name cannot be empty")
        self._name = value

    @name.deleter
    def name(self) -> None:
        del self._name

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {_escape_markdown(self._name)}>"


def _escape_markdown(text: str) -> str:
    markdown_chars = {"*", "[", "]", "(", ")", ".", "#"}
    escaped_text = ""
    escape_next = False
    for char in text:
        if escape_next:
            escape_next = False
            escaped_text += char
        elif char in markdown_chars:
            escaped_text += f"\{char}"
        else:
            escaped_text += char
    return escaped_text


# ── Annotations ───────────────────────────────────────────────────────────────

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

AnyDict: TypeAlias = "Mapping[Any, Any]"
