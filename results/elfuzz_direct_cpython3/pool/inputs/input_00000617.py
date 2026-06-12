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


class SingletonMeta(type):
    """
    Metaclass that makes a class behave like a singleton.
    """

    _instances: dict[type[object], object] = {}

    def __call__(cls: type[Singleton]) -> Singleton:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """"""


class SimpleDescriptor:
    """Simple descriptor."""

    owner_class: ClassVar[Type[Any]]

    def __set_name__(self, owner: Any, name: str) -> None:
        self.owner_class = type(owner)
        self.name = name

    def __get__(self, instance: Any, owner: Type[Any]) -> Any:
        if instance is None:
            return self
        result = getattr(instance.__dict__, self.name)
        setattr(instance.__dict__, self.name, self.owner_class(result))
        return result


@functools.cache
def cached_property(fun: Callable[..., T]) -> PropertyWrapper:
    """Decorator for caching property values."""
    return PropertyWrapper(name=fun.__name__, fun=fun)


class PropertyWrapper:
    """Class to hold information about cached properties."""

    def __init__(self, *, name: str, fun: Callable[..., T]):
        self.name = name
        self.fun = fun

    def __get__(self, instance: Any, owner: Type[Any]) -> T:
        assert isinstance(self.name, str)
        value = self.fun(instance)
        return value


# ─── Context Managers ────────────────────────────────────────────────────────


class FileContextManager:
    """A file context manager.

    The ``with`` statement can be used with this class to manage opening and closing of files.
    """

    def __init__(self, filename: str, mode: str) -> None:
        self.filename = filename
        self.mode = mode
        self.file: Optional[IO[Any]] = None

    def open_file(self) -> IO[Any]:
        return open(self.filename, mode=self.mode)

    def close_file(self) -> None:
        if self.file is not None:
            self.file.close()

    def __enter__(self) -> IO[Any]:
        print(f"Opening {self.filename}...")
        self.file = self.open_file()
        return self.file

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: TracebackType,
    ) -> Literal["return", "raise", "ignore"]:
        print(f"Closing {self.filename}.")
        self.close_file()
        return False


@contextlib.contextmanager
def context_manager(filename: str, mode: str) -> Generator[IO[Any], None, None]:
    """Callable that returns a context manager for managing opening and closing of files.

    This function should be called using the ``yield`` keyword within a ``with`` statement when needed.
    """

    print(f"Opening {filename}...")
    try:
        file_handle = open(filename, mode=mode)
        yield file_handle
    finally:
        print(f"Closing {filename}.")
        file_handle.close()


def generate_fibonacci_series(n: int) -> Iterator[int]:
    """Generates a Fibonacci series up until `n` elements."""
    a, b = 0, 1
    for i in range(2, n + 1):
        yield b
        a, b = b, a + b


# ── Classes ──────────────────────────────────────────────────────────────────
