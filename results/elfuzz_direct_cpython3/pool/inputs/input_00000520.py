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
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()  # sentinel value for missing values in caches.


# ─── Clases abstractas ───────────────────────────────────────────────────────

class BaseClass(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def class_method(cls):
        ...
    

# ─── Metaclasses ─────────────────────────────────────────────────────────────

class Singleton(metaclass=abc.ABCMeta):
    @classmethod
    def instance(cls, *args, **kwargs):
        return cls._instance(*args, **kwargs)
    
    @classmethod
    @abc.abstractmethod
    def _instance(cls, *args, **kwargs):
        ...


class MetaSingleton(type):

    _instances: dict[type, Singleton] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# ─── Generators ──────────────────────────────────────────────────────────────


class InfiniteGenerator(Generic[T]):
    def __init__(self, iterable: Iterable[T]) -> None:
        self.iterable = iter(iterable)

    def __iter__(self) -> Generator[T, None, None]:
        yield from iter(self.iterable)

    def __next__(self) -> T:
        try:
            return next(self.iterable)
        except StopIteration as e:
            self.iterable = iter(self.iterable)
            return next(self.iterable)


def generator_function(n: int) -> Generator[int, None, None]:
    numbers = list(range(1, n + 1))
    index = 0
    while True:
        if index == len(numbers):
            index = 0
        yield numbers[index]
        index += 1


def infinite_generator(start: int, step: int) -> Generator[int, None, None]:
    while True:
        yield start
        start += step


# ─── Decorators ──────────────────────────────────────────────────────────────
   
def debug(func):
    """
    Print the function signature and return value.
    """

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]  # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)  # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (TYPE_CHECKING, Any, Callable, Dict, Generic, List, NamedTuple, Optional, Protocol, Sequence, Tuple,
                    TypeVar, Union)

if TYPE_CHECKING:
    from typing_extensions import ParamSpec # noqa: F401


class ExampleEnum(enum.Enum):
    A = 'a'
    B = 'b'
    C = 'c'


@dataclasses.dataclass(frozen=True)
class DataClassExample():
    foo: str
    bar: int
    baz: float
    

def func_with_default_args(arg1=1, arg2=int()):
    pass


def main():
    
    awaitable_example()
    protocols_example()
    
    example_data_classes()


# Awaitables -------------------------------------------------------------

async def wait_for(seconds: float) -> None:
    await asyncio.sleep(seconds)


async def get_random_number(min_num: float, max_num: float) -> float:
    return random.uniform(min_num, max_num)


async def run_async_tasks(tasks: Sequence[Callable[..., Any]]) -> None:
    tasks_to_run = []
    for task in tasks:
        if asyncio.iscoroutinefunction(task):
            tasks_to_run.append(asyncio.ensure_future(task()))
        else:
            raise TypeError('task must be a coroutine function')
            
    done, pending = await asyncio.wait(tasks_to_run, return_when=asyncio.FIRST_COMPLETED)
    for future in done:
        print(future.result())

        
def awaitable_example():
    @dataclasses.dataclass(frozen=True)
    class Task(NamedTuple):
        name: str
        start_time: float
        
    tasks = [
        lambda x=3.5: wait_for(x),
        lambda y=10.8, z=6.7: sum((x, y, z)),
        lambda num: get_random_number(0.0, 10.0), 
    ]
    
    
    print('\n--- Awaitable tasks ---\n')
    for task in tasks:
        print(f'{type(task).__name__}({repr(task.__defaults__)})')

    print('\n=== Running the tasks ===\n')
    tasks_names = [str(type(t).__name__).replace('_', ' ').capitalize().strip() for t in tasks]
    tasks_start_time = [time.time()] * len(tasks)
    tasks_result = []
    total_elapsed_time = 0
    
    while True:
        elapsed_time = time.time() - tasks_start_time.pop(0)
        total_elapsed_time +=