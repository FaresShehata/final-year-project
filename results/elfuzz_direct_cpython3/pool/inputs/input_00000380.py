"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
from typing import Any, Callable, Generic, Iterable, Iterator, TypeVar


# ─── DESCRIPTION ────────────────────────────────────────────────────────────────


"""This is the first seed. It contains three sections:

- Section 1 describes how to use object-oriented programming.
- Section 2 introduces metaclasses.
- Section 3 shows how to use descriptors.


These are all part of the course's Object-Oriented Programming lesson.

"""


# ─── SECTION 1: OBJECT-ORIENTED PROGRAMMING ────────────────────────────────────


class Person:
    """A person, with name and age attributes."""

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


p: Person = Person("John Doe", 42)


# ─── SECTION 2: METACLASSES ────────────────────────────────────────────────────


class Meta(type):
    """Metaclass for testing purposes."""

    def __new__(
        metacls: type, classname: str, bases: tuple[type], namespace: dict[str, Any]
    ) -> type:
        print(
            f"Creating new instance of 'Meta' "
            f"class '{classname}' from base classes: "
            f"{', '.join(str(base.__name__) for base in bases)}"
        )
        return super().__new__(metacls, classname, bases, namespace)

    def __init__(cls: type, classname: str, bases: tuple[type], namespace: dict[str, Any]) -> None:
        print(f"Initializing class '{classname}'")
        super().__init__(classname, bases, namespace)

    def __call__(cls: type, *args: Any, **kwds: Any) -> type:
        print(f"Calling '__call__' method for class '{cls.__name__}'")
        obj = super().__call__(*args, **kwds)
        print(f"'{obj}' created.")
        return obj


class A(metaclass=Meta):
    """Class 'A' which inherits from 'Meta'."""


a: A = A()

# ─── SECTION 3: DESCRIPTORS ────────────────────────────────────────────────────


T = TypeVar("T")


class TypedDescriptor(Generic[T]):
    """A descriptor which ensures that only objects of certain types can be used."""

    def __init__(self, expected_type: type, lo: T | None    """
    return TypedDescriptor(expected_type, lo=lo, hi=hi)


@contextlib.contextmanager
def checked_range(lo: int | float, hi: int | float) -> Generator[None, None, None]:
    """Context manager that checks whether its contents were within a range."""
    try:
        yield
    except TypeError as e:
        raise TypeError(f"{e.args[0]} in {range(lo, hi)}")


def check_subclass(cls: type, expected_class: type) -> bool:
    """Return True iff cls is a subclass of expected_class."""
    return issubclass(cls, expected_class)

# ── Context managers ──────────────────────────────────────────────────────────


class ClosableMixin:
    """A mixin class for classes with resources that need closing."""

    _closed: bool = False

    @property
    def closed(self) -> bool:
        return self._closed

    def close_resource(self) -> None:
        pass

    def close(self) -> None:
        if self.closed:
            return
        # TODO: implement actual resource closure mechanism (for example,
        # using a context manager)
        print(f"{self} being closed.")
        self.close_resource()
        self._closed = True

    def __del__(self) -> None:
        self.close()


class OpenedFile(ClosableMixin):
    """A file open for reading and writing."""

    def __init__(
        self, filename: str, mode="r", encoding="utf-8"
    ) -> None:
        super().__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.fh = open(filename, mode=mode, encoding=encoding