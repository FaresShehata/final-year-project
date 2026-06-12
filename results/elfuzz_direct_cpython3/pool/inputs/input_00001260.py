"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroups, etc.
"""

from enum import Enum as _enum, auto
import enum
from inspect import isfunction
import itertools
import math
from pathlib import Path
from types import FunctionType
from typing import (
    Any,
    ClassVar,
    Optional,
    Union,
    Dict,
    List,
    Set,
    Tuple,
    Iterable,
    Generic,
    TypeVar,
    Callable,
    Type,
    cast,
    NoReturn,
    Literal,
    TypedDict,
    final,
    ParamSpec,
    get_args,
    get_origin,
)
import warnings

from collections import defaultdict
from functools import wraps
from typing import (
    runtime_checkable,
    Protocol,
    get_type_hints,
    get_args,
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
    @classmethod
    def from_json(cls, json_str: str) -> T:
        """Parse a JSON string and turn it into an instance of this class."""
        ...

    @property
    def to_json(self) -> str:
        """Turn the object into a JSON string."""
        ...


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person(object):
    name: str
    age: int
    sex: str = "male"


@dataclasses.dataclass(order=True)
class Student(Person):
    grade: float

    @property
    def full_name(self) -> str:
        return f"{self.name} ({self.grade})"


# ── Slots ──────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class Planet(object):
    name: str
    size: float = 3.844e+6
    mass: float = 1.989e+30
    gravity: float = 1.622

    @property
    def density(self) -> float:
        volume = (4 / 3 * math.pi * self.size ** 3) / 1_000_000_000
        return self.mass / volume


# ── Structural pattern matching ────────────────────────────────────────────────

def get_status(status: Status) -> dict[str, str]:
    status_map = {
        Status.PENDING : {"message": "status not yet determined"},
        Status.RUNNING : {"message": "status running"},
        Status.SUCCESS : {"message": "success"},
        Status.FAILED   : {"message": "failure"},
        Status.CANCELLED: {"message": "cancelled"}
    }

    if status in status_map:
        return status_map[status]

    raise ValueError(f"Invalid status: {status}")


# ── Walrus operator ────────────────────────────────────────────────────────────

def find_persons_with_age(persons: list[Person], age: int) -> bool:
    for person in persons:
        if person.age == age:
            return True

    return False


async def find_persons_with_age_async(persons: list[Person], age: int) -> bool:
    for person in persons:
        if person.age == age