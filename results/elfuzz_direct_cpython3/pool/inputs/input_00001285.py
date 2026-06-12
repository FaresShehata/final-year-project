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
import uuid
from collections import deque
from functools import partial
from itertools import chain, count, cycle, islice, zip_longest
from math import ceil, floor, log2
from numbers import Number
from pathlib import Path
from statistics import median
from types import ModuleType
from typing import (
    Any,
    AsyncIterator,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    FrozenSet,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)


# ──────────── Types ────────────────────────────────────────────────────────────────


class Bool(enum.Enum):
    False_ = 0
    True = 1


YIELD_FROM = object()


# ─────────── Decorators ────────────────────────────────────────────────────────


def noop(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]: ...
"""No operation function that accepts only a coroutine"""


async def pipeline(*coros: Coroutine[Any, Any, T]) -> T:
    """
    A helper to simplify the writing of asynchronous pipelines.
    """
    for coro in coros[:-1]:
        await coro
    return await coros[-1]


def retry(times=3, interval=1):
    """
    A decorator that retries a function call when it fails.

    Args:
        times: The number of times to retry the function. Defaults to 3.
        interval: The number of seconds to wait between each retry attempt. Defaults to 1.
    """

    def wrapper(func):
        async def wrapper_retry(*args, **kwargs):
            attempts = 0
            while attempts < times:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= times:
                        raise e
                    await asyncio.sleep(interval)
            return await func(*args, **kwargs)

        return wrapper_retry

    return wrapper


def measure_time(func):
    """
    A decorator that measures the execution time of a function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.4f} seconds.")
        return result

    return wrapper


# ─────────── Classes ───────────────────────────────────────────────────────────

class FileIOError(Exception):
    """
    An error raised by file I/O operations. Inherits from :py:class:`Exception`.
    """

    def __str__(self):
        return "File IO Error"


class InvalidInputError(ValueError):
    """
    An error raised for invalid input. Inherits from :py:class:`ValueError`. 
    """

    def __str__(self):
        return "Invalid Input"


class RecursiveLoopError(RuntimeError):
    """
    An error raised when a recursive loop is detected. Inherits from :py:class:`RuntimeError`.
    """

    def __str__(self):
        return "Recursive Loop Detected"

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


class CachedProperty(TypedDescriptor):
    """A property whose value is computed once per instance and then replaced."""
    
    def __init__(self, func):
        self.func = func
        self.name: str = ""
        
    def __set_name__(self, owner, name):
        self.name = name
        
    def __get__(self, obj, cls):
        if obj is None:
            return self
        val = obj.__dict__[self.name] = self.func(obj)
        return val


# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(type):

    def __prepare__(metacls, name, bases, **kwargs):  # type: ignore[misc]
        return {}

    def __new__(
            metacls,
            name: str,
            bases: tuple[type],
            namespace: dict[str, Any],
            **kwargs: Any,
    ) -> Type[T]:
        if "__module__" in namespace or "__qualname__" in namespace:
            del namespace["__module__"]
            del namespace["__qualname__"]

        if "__slots__" in namespace:
            slots = namespace.pop("__slots__")
            attrs = {}
            for attr in slots:
                attr = attr.strip()
                attrs[attr] = TypedDescriptor(TypeVar(attr))
            namespace.update(attrs)

        print(namespace)
        cls = super().__new__(metacls, name, bases, namespace)
        cls._registry = {}
        for base in reversed(bases):
            reg_cls = registry(base)
            if reg_cls:
                reg_cls.register(cls)
        return cls


def registry(target: type) -> Optional[ClassVar[list]]:
    def decorator(cls: type):
        try:
            target._registry.append(cls)
        except AttributeError:
            target._registry = [cls]
        return cls
    return decorator


@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions as e:
        pass


# ─── ApplicationContext ──────────────────────────────────────────────────────

class ApplicationContext(object):

    def __init__(self, *argv, **env):
        self.argv = argv
        self.env = env

    @property
    def args(self):
        return self.argv + list(sys.argv[1:])

    @property
    def kwargs(self):
        env = {
            k: v
            for k, v in self.env.items() 
            if k.startswith("_") and (v := os.environ.get(k)) != None
        }
        return {k.replace("_", "-"): v for k, v in env.items()}

    def get_env(self, key):
        return self.kwargs[key]

    def set_env(self, key, value):
        return self.kwargs.setdefault(key, value)

    def run(self, func):
