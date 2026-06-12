"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import inspect
import itertools
import operator
import os
import pathlib
import pickle
import random
import re
import string
import typing as t
import weakref
from collections.abc import (
    Awaitable,
    Callable,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Set,
    MutableMapping,
)
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime, timedelta
from enum import Enum, auto, unique
from enum import (
    IntEnum,
    IntFlag,
    IntDescriptionMixin,
    StrEnum,
    ReprEnum,
    IntFlags,
)
from enum_tools import EnumMeta
from enum_tools.enum_tools import EnumToolsMeta
from enum_tools.repr_enum import ReprEnumMeta


def _get_json_encoder_class() -> type[json.JSONEncoder]:
    """Get the JSON encoder class."""
    try:
        from json.encoder import JSONEncoder

        return JSONEncoder
    except ImportError:
        pass

    try:
        from jsonlib.jsonencoder import JSONEncoder

        return JSONEncoder
    except ImportError:
        pass

    raise RuntimeError("No JSON encoder found.")


JSONEncoderType = t.TypeVar("JSONEncoderType", bound=t.Type[_get_json_encoder_class()])


class CustomJSONEncoder(_get_json_encoder_class()):
    """Custom JSON encoder."""

    def default(self, o) -> t.Any:
        if hasattr(o, "__dict__"):
            return vars(o)
        else:
            return super().default(o)


# https://stackoverflow.com/a/38739695
class MyDataClass(dataclasses.Dataclass):

    @classmethod
    def fields(cls) -> tuple[dataclasses.Field, ...]:
        return dataclasses.fields(cls)

    @classmethod
    def defaults(cls) -> dict[str, t.Any]:
        return {
            attr.name: getattr(cls(), attr.name) for attr in cls.fields() if attr.default is not dataclasses.MISSING
        }


@unique
class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()


@unique
class TaskPriority(IntFlag):
    LOWEST = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    HIGHEST = auto()


@dataclass
class Task(MyDataClass):
    id_: int = field(default_factory=lambda: get_task_id())
    name: str
    priority: TaskPriority = TaskPriority.LOW
    status: TaskStatus = TaskStatus.PENDING
    started_at: datetime | None = None
    finished_at: datetime | None = None

    def start(self) -> None:
        self.started_at = datetime.now()

    def finish(self) -> None:
        self.finished_at = datetime.now()

    def __repr__(self) -> str:
        return f"<Task {self.id_} - {self.name}>"

    @property
    @functools.lru_cache(maxsize=128)
    def duration(self) -> timedelta:
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        elif self.started_at:
            return datetime.now() - self.started_at
        else:
            return timedelta(seconds=random.randint(1, 10))

    @staticmethod
    def get_next_id(task_list: list[Task]) -> int:
        next_id = max((t.id_ for t in task_list), default=-1) + 1
        return next_id


def generate_unique_name(prefix: str, n_chars: int = 4) -> str:
    """Generate a unique name."""
    chars = string.ascii_uppercase + string.digits
    while True:
        yield prefix + "".join(random.choice(chars) for _ in range(n_chars))


class JsonSerializable(t.ABC):
    @t.overload
    @classmethod
    def load_from_file(cls, path: str, **kwargs: t.Any) -> JsonSerializable:
        ...

    @t.overload
    @classmethod
    def load_from_file(cls, path: pathlib.Path, **kwargs: t.Any) -> JsonSerializable:
        ...

    @classmethod
    def load_from_file(cls, path: str | pathlib.Path, **kwargs: t.Any) -> JsonSerializable:
        with open(path, "r") as file:
            kwargs.update(json.load(file))
            return cls(**kwargs)


class PickleSerializable(JsonSerializable):
    @classmethod
    def load_from_file(cls, path: str, **kwargs: t.Any) -> PickleSerializable:
        with open(path, "rb") as file:
            kwargs.update(pickle.load(file))
            return cls(**kwargs)


class RandomString:
    def __init__(self, length: int = 10, chars: str = string.ascii_letters + string.digits) -> None:
        self.length = length
        self.chars = chars

    def __call__(self) -> str:
        return "".join(random.choices(self.chars, k=self.length))


@contextlib.contextmanager
def timer(name: str):
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    print(f"{name}: {end_time-start_time}")


class TimerContextManager:
    def __enter__(self) -> None:
        self.start_time = datetime.now()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: traceback.TracebackType | None,
    ) -> None:
        end_time = datetime.now()
        print(f"TimerContextManager: {exc_type}, {exc_val}, {exc_tb}")
        print(f"Elapsed time: {end_time-self.start_time}")


def main():
    # task_list = [
    #     Task(id_=i, name=f"Task{i}", priority=TaskPriority.HIGH, status=TaskStatus.RUNNING) for i in range(10)
    # ]
    #
    # task_list.sort(key=lambda x: x.duration, reverse=True)
    #
    # print(task_list)
    # print(get_next_id(task_list))

    # path = "./my_data.json"
    # task = Task(id_=5, name="My Task", priority=TaskPriority.LOW, status=TaskStatus.COMPLETED)
    # task.save_to_file(path)

    # task = Task.load_from_file(path)
    # print(task)

    # task =def count_up():
    global count
    count += 1
    return count


# Pass a Python list of integers `numbers` into the `map()` function to double each element in the list.
list(map(lambda x: x*2, [1, 4, 5]))


# Multiply every element in the list `numbers` by 2.
[lambda x: x * 2(number) for number in numbers]


# Use the generator from the previous seed to calculate prime numbers.
prime_generator = primes()