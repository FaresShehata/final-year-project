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
    Dict,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

if TYPE_CHECKING:
    from types import TracebackType


class Color(enum.Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclasses.dataclass(frozen=True)
class Person:
    first_name: str
    last_name: str
    age: int
    email: str
    phone_number: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    birth_date: datetime.date
    favorite_colors: Optional[Set[str]] = None
    pets: Optional[List["Pet"]] = None
    job_title: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None


@dataclasses.dataclass(frozen=True)
class Pet:
    name: str
    type: str
    age: int
    owner: Person
    color: str
    breed: Optional[str] = None
    weight_kg: float = 1.0


def get_person() -> Person:
    return Person(
        first_name="John",
        last_name="Doe",
        age=42,
        email="john.doe@example.com",
        phone_number="555-1234",
        address="123 Main St.",
        city="Anytown",
        state="CA",
        zip_code="12345",
        country="USA",
        birth_date=datetime.date(1978, 6, 1),
        favorite_colors=None,
        pets=[],
        job_title="Software Engineer",
        company="Example Co.",
        salary=50000.0,
    )


@dataclasses.dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclasses.dataclass(frozen=True)
class Vector(Generic[T]):
    start: T
    end: T


PointVector = Vector(Point)


def add_point_vector(point_vector: PointVector) -> float:
    delta_x = point_vector.end.x - point_vector.start.x
    delta_y = point_vector.end.y - point_vector.start.y
    return math.sqrt(delta_x**2 + delta_y**2)


PointVector = Vector(Point)


@dataclasses.dataclass(frozen=True)
class MyEnum(enum.IntEnum):
    A = 1
    B = 2
    C = 3


# ── builtins ───────────────────────────────────────────────────────────────────

def is_animal(animal: Animal) -> bool:
    return animal in {Dog(), Cat()}  # noqa


def get_color(color: Color) -> str:
    match color:
        case Color.RED:
            print("Red")
        case Color.GREEN:
            print("Green")
        case Color.BLUE:
            print("Blue")


def describe_pet(pet: Pet) -> str:
    match pet:
        case Pet(name=name, type=type_, age=age, owner=owner, color=color, breed=breed, weight_kg=weight_kg):
            print(f"{name} is a {type_} that weighs {weight_kg:.2f} kg.")


def draw_pet(pet: Pet) -> None:
    match pet:
        case Dog(name, age, *_) if age < 5:
            draw_small_dog(name)
        case Dog(*_, age) if age > 5:
            draw_big_dog()
        case _:
            draw_unknown_dog()


def test_pattern_matching():
    for i in range(10):
        p = random.choice([Cat(), Dog()])
        match p:
            case Dog(name, age, *_) if age < 5:
                print(f"Small dog named {name}.")
            case Dog(*_, age) if age > 5:
                print(f"Loud dog named {p.name}.")
            case _:
                print(f"Unknown dog named {p.name}.")


def test_structural_pattern_matching():
    for i in range(10):
        p = random.choice    nlines = obj.co_firstlineno - 1
    lines = inspect.getsourcelines(obj)[0][nlines:]
    return lines, nlines


def get_bytecode(obj: object) -> bytes:
    return marshal.dumps(obj.co_code)


# ── ctors & destructors ───────────────────────────────────────────────────────

def make_nonzero(x: object, y: object) -> bool:
    if x != y:
        return True
    else:
        raise ValueError("zero")


