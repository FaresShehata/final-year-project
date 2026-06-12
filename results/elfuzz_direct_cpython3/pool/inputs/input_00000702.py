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

    def __str__(self) -> str:
        return f"priority{self.value}"


# ── Classes ───────────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    height_m: float
    weight_kg: float

    @property
    def bmi(self) -> float:
        return self.weight_kg / (self.height_m ** 2)


PersonList = list[Person] | set[Person]
def add_person(person_list: PersonList, person: Person) -> None:
    if isinstance(person_list, set):
        person_list.add(person)
    else:
        bisect.insort_left(person_list, person)

def get_average_height(
    person_lists: tuple[list[Person], ...],
) -> float:
    heights = [person.height_m for p_list in person_lists for person in p_list]

    total = sum(heights)
    average = total / len(heights)
    return round(average, 2)


PeopleDict = dict[str, Person]
def get_oldest_people(
    people_dict: PeopleDict,
) -> list[tuple[str, Person]]:
    ages = [(p.age, p.name) for n, p in people_dict.items()]
    ages.sort(reverse=True)
    oldest_names = [n for _, n in ages[:3]]
    oldest_people = [people_dict[n] for n in oldest_names]
    return oldest_people


# ── Generics ──────────────────────────────────────────────────────────────────

@runtime_checkable
class Command(Protocol[T]):
    def execute(self) -> T:
        ...


CommandResult = type[asyncio.Future[int]]()


class SimpleCommand(Command[int]):
    def __init__(
        self,
        *,
        delay_ms: int,
    ) -> None:
        self.delay_ms = delay_ms

    def execute(self) -> int:
        time.sleep(self.delay_ms / 1000.0)
        return 42


class ComplexCommand(Command[CommandResult]):
    def __init__(
        self,
        *,
        command_a: Command[Awaitable[CommandResult]],
        command_b: Command[Awaitable[CommandResult]],
    ) -> None:
        self.command_a = command_a
        self.command_b = command_b

    def execute(self) -> CommandResult:
        yield from self.command_a.execute()
        yield from self.command_b.execute()

        return await asyncio.gather(*[command.execute() for command in (self.command_a, self.command_b)])


# ── Dataclasses ───────────────────────────────────────────────────────────────