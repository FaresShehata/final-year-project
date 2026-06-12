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


class Person(metaclass=abc.ABCMeta):
    @classmethod
    def _new(cls, *args: Any, **kwargs: Any) -> Person:
        obj = super().__new__(cls)
        cls._init(obj, *args)

        return obj

    def _init(self, *args: Any, **kwargs: Any) -> None:
        pass

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._validate_name(value)
        self._name = value

    def _validate_name(self, value: str) -> None:
        raise NotImplementedError("_validate_name is not implemented")

    def __eq__(self, other: object) -> bool:
        return type(other) == type(self) and other.name == self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}(name={self.name})"

    def __str__(self) -> str:
        return self.__repr__()

    @staticmethod
    def _create(name: str) -> Person:
        return Person._new(name=name)

    @classmethod
    def _is_valid_name(cls, name: str) -> bool:
        return True

    @classmethod
    def create(cls, name: str) -> Person:
        if not cls._is_valid_name(name):
            raise ValueError(f"Name '{name}' is not valid.")

        return cls._create(name=name)

    @classmethod
    def validate_name(cls, name: str) -> None:
        if not cls._is_valid_name(name):
            raise ValueError(f"Name '{name}' is not valid.")


class Student(Person):
    _school: ClassVar[str]

    def __init__(self, name: str, school: str = "Miss Mary's School") -> None:
        self.school = school

        self._super_init(name=name, school=school)

    def _super_init(self, *args: Any, **kwargs: Any) -> None:
        super()._init(*args, **kwargs)

    @property
    def school(self) -> str:
        return self._school

    @school.setter
    def school(self, value: str) -> None:
        self._validate_school(value)
        self._schoolSeed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          decorators, context managers
"""


def gcd(a: int, b: int) -> int:
    """Euclidean algorithm for greatest common divisor."""
    while a != 0 and b != 0:
        if a > b:
            a %= b
        else:  # a < b
            b %= a

    return max(a, b)


@gcd
def find_gcd(*numbers: int) -> int:
    """Find the greatest common divisor of all numbers passed as arguments."""
    if not numbers:
        raise ValueError("At least one argument required.")

    return functools.reduce(gcd, numbers)


find_gcd(48, 64, 72)


class Money(float):
    def __new__(cls, dollars: float, cents: int) -> Money:
        return float.__new__(cls, dollars + cents / 100)

    def __float__(self) -> float:
        return float(super())

    def __int__(self) -> int:
        return int(super())


Money(100, 10)


class Text(str):
    def __new__(cls, text: str, language: str) -> Text:
        return str.__new__(cls, text)

    def __str__(self) -> str:
        return f"{self.language} translation of '{super()}'"


Text("Hello", "English")
Text("Bonjour", "French")

Text("Hello", "English").language


class Tag(object):
    def __init__(self, tag_type: str): ...
    def __enter__(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb): ...


with Tag("h1"):
    print("Heading")
print(Tag("p"))

with Tag("div") as div_tag:
    with Tag("span") as span_tag:
        print(div_tag, span_tag)


class MyContextManager(contextmanager):
    def __call__(self, function: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        with self.opened_object(function, args, kwargs) as opened_object:
            return function(opened_object, *args, **kwargs)


class MyOpen:
    def __init__(self, filename: str, mode: str) -> None:
        self.filename = filename
        self.mode = mode

    def __enter__(self) -> MyOpen:
        print("__enter__()")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        print("__exit__()")

    def read(self) -> str:
        print("\tReading...")
        return ""

    def write(self, content: str) -> None:
        print(f"\tWriting {len(content)} bytes...")

    def close(self) -> None:
        print("\tClosing...")


class MyFileWriter(MyOpen):
    def __init__(self, path:    LOW    = 1
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
    status: Status = Status.PENDING
    start_time: float = 0.0
    end_time: float = 0.0

    def __post_init__(self):
        if not isinstance(self.priority, Priority):
            raise ValueError(f"Invalid Priority: '{self.priority}'")


@dataclasses.dataclass(order=True, frozen=True, slots=True)
class TaskRunResult(Generic[T]):
    task_id: int
    result: T
    exc_info: tuple[Exception, BaseException, TracebackType] | None = None


# ── Collections ────────────────────────────────────────────────────────────────

def _random_int() -> int:
    return random.randint(-99_999, 99_999)


def _add_to_heap(heap: list[tuple[int, K]], item: K, key: Callable[[K], int]) -> None:
    bisect.insort_left(heap, (key(item), item))


async def _sleep_and_add(heap: list[tuple[int, K]], seconds: float) -> None:
    await asyncio.sleep(seconds)
    _add_to_heap(heap, _random_int(), lambda x: abs(x - _random_int()))


def _run_tasks(tasks: set[Task]) -> set[Task]:
    for task in tasks:
        task.status = Status.RUNNING
        task.start_time = time.time()

    return tasks


async def _wait_for_task(task: Task) -> None:
    while task.status.is_terminal():
        await asyncio.sleep(0.01)


async def _check_end_times_and_update_status(
    heap: list[tuple[int, K]],
    results: deque[TaskRunResult[K]],
    finished_tasks: set[Task],
) -> None:
    while len(results) > 0 and results[0].task_id == finished_tasks.pop().id:
        result = results.popleft()
        if result.exc_info:
            task = [t for t in finished_tasks if t.id == result.task_id][0]
            task.status = Status.FAILED
            task.end_time = time.time()
        else:
            task = [t for t in finished_tasks if t.id == result.task_id][0]
            task.status = Status.SUCCESS
            task.end_time = time.time()


async def _process_results(
    heap: list[tuple[int, K]],
    results: deque[TaskRunResult[K]],
    finished_tasks: set[