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

    name: str
    fun: Callable[..., T]

    def __init__(self, *, name: str, fun: Callable[..., T]) -> None:
        self.name = name
        self.fun = fun

    @property
    def value(self) -> T:
        return self.fun()

    def __get__(self, obj: object, _: type | None) -> T:
        return self.value


# ── Generators ────────────────────────────────────────────────────────────────


class ChildGeneratorContextManager(contextlib.AbstractContextManager):

    """A context manager which yields its child generator.

    It can only be used as an iterator, with the `next` built-in function or
    the `send` method.
    """

    def __init__(self, gen: Generator) -> None:
        self.gen_ref = weakref.ref(gen)  # type: ignore[arg-type]

    def __enter__(self) -> Generator:
        return next(self.gen_ref())

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: traceback.TracebackType | None,
    ) -> Literal["return"] | Literal["ignore"]        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

