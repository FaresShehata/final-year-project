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
    """A descriptor which enforces a particular type.
    """
    attr_type: Type[Any]

    def __init__(self, name: str) -> None:
        self.name = "_" + name

    def __set_name__(self, owner: Type[T], name: str) -> None:
        self.storage_name = f"_{owner.__name__}{name}"

    def __get__(self, obj: T, cls: Optional[Type[T]] = None) -> Any:
        if not obj:
            return self
        return getattr(obj, self.storage_name)

    def __set__(self, obj: T, value: Any) -> None:
        if not isinstance(value, self.attr_type):
            raise TypeError(f"{value} is not of type {self.attr_type}")
        setattr(obj, self.storage_name, value)


class Integer(TypedDescriptor):
    "Enforces that the attribute be an integer."
    attr_type = int


class Float(TypedDescriptor):
    "Enforces that the attribute be an integer."
    attr_type = float


class String(TypedDescriptor):
    "Enforces that the attribute be an string"
    attr_type = str


class PositiveInteger(Integer):
    "Enforces that the attribute be positive integer"

    def __set__(self, obj: T, value: int) -> None:
        if value <= 0:
            raise ValueError("Value must be greater than zero")
        super().__set__(obj, value)


class PositiveFloat(Float):
    "Enforces that the attribute be a positive float."

    def __set__(self, obj: T, value: float) -> None:
        if value < 0:
            raise ValueError("Value must be greater than or equal to zero.")
        super().__set__(obj, value)
        

class NegativeFloat(Float):
    "Enforces that the attribute be a negative float."

    def __set__(self, obj: T, value: float) -> None:
        if value >= 0:
            raise ValueError("Value must be less than or equal to zero.")
        super().__set__(obj, value)


class NonEmptyString(String):
    "Enforces that the attribute be non-empty string"

    def __set__(self, obj: T, value: str) -> None:
        if not len(value.strip()):
            raise ValueError("Value cannot be empty")
        super().__set__(obj, value)


# ── Classes and instances ───────────────────────────────────────────────────async def main() -> None:
    for _ in range(3):
        print(await get_random_number())
        await sleep(1.0)


async def get_random_number() -> float:
    return random.random()


asyncio.run(main())


# ── Protocols ───────────────────────────────────────────────────────────────

P = TypeVar("P")


@runtime_checkable
class Iterable(P):
    ...  # pragma: no cover

@runtime_checkable
class Container(P):
    ...  # pragma: no cover

@runtime_checkable
class Sized(P):
    def __len__(self) -> int: ...
    ...  # pragma: no cover

@runtime_checkable
class Reversible(P):
    ...  # pragma: no cover

@runtime

def process_count():
    with lock_for(Process):
        return multiprocessing.cpu_count()


_process_lock: Lock = Lock()

if TYPE_CHECKING:
    from subprocess import Process

else:

    # noinspection PyShadowingNames
    class Process(metaclass=ABCMeta):
        def terminate(self):
            pass

        @property
        def pid(self):
            ...

        @property
        def exitcode(self):
            ...

        def wait(timeout=None):
            ...

        def communicate(input=None, timeout=None):
            ...


try:
    from concurrent.futures import ThreadPoolExecutor as Executor

except ImportError:
    from threading import Thread

    from future_builtins import map

