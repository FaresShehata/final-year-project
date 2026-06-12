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

@runtime_checkable
class HasStatus(Protocol[K]):
    status: Status

# ── Data Classes ────────────────────────────────────────────────────────────


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int | float
    is_married: bool = False

p1 = Person(name="Alice", age=30)
p2 = Person(name="Bob", age=25)
print(p1.name)
print(p1.age)
print(p1.is_married)


@dataclasses.dataclass(frozen=False)
class Employee(Person):
    salary: int | float

e1 = Employee(name="Charlie", age=40, salary=60_000.0)
print(e1.salary)

try:
    e1.salary = 70_000.0
except Exception as e:
    print(e)

def get_age(person: Person) -> int | float:
    return person.age

def get_salary(employee: Employee) -> int | float:
    return employee.salary

assert get_age(p1) == p1.age
assert get_salary(e1) == e1.salary
#assert get_salary(p1) == p1.salary  # error


@dataclasses.dataclass(slots=True)
class Student(Person):
    grade: int | float

s1 = Student(name="David", age=18, grade=90)
print(s1.grade)

def set_grade(student: Student, grade: int | float) -> None:
    student.grade = grade

set_grade(s1, 95)
print(s1.grade)


# ── Generics ────────────────────────────────────────────────────────────────


T = TypeVar("T")


def safe_divide(x: T, y: T) -> T:
    if isinstance(y, (int, float)):
        assert not y == 0, "Division by zero!"
        return x / y
    else:
        raise TypeError(f"{x} and {y} must be numbers!")


def safe_divide_generic[T: int | float](x: T, y: T) -> T:
    if isinstance(y, (int, float)) and y != 0:
        return x / y
    else:
        raise TypeError(f"{x} and {y} must be numbers!")


safe