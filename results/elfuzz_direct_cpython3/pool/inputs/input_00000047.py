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
        owner.__dict__[self.name] = self

    @property
    def value(self) -> Any:
        return getattr(self.owner(), self.name)

    @value.setter
    def value(self, val: Any) -> None:
        if not isinstance(val, self.expected_type):
            raise TypeError(f"{val} must be an instance of {self.expected_type}")
        if self.lo is not None and val < self.lo:
            raise ValueError(f"{val} must be >= to {self.lo}")
        if self.hi is not None and val > self.hi:
            raise ValueError(f"{val} must be <= to {self.hi}")
        setattr(self.owner(), self.name, val)


def typed(*expected_types: type) -> Callable[[Any], Any]:
    """
    Decorator for defining typed properties.

    :param expected_types: The expected types of the property. If more than one type is provided,
                           all types are checked.
    """

    def decorator(cls: Any) -> Any:
        assert hasattr(cls, "__slots__"), "Typed descriptor can only be used with slots classes"

        for slot in cls.__slots__:
            expected_type = expected_types[0]
            if len(expected_types) > 1:
                expected_type = expected_types[itertools.count().next()]

            name = slot.replace("__", "")
            descriptor = TypedDescriptor(expected_type)
            descriptor._setter(descriptor.value)
            setattr(cls, slot, descriptor)

        return cls

    return decorator


# ── Metaclasses ───────────────────────────────────────────────────────────────

class Meta(type, abc.ABCMeta):
    """
    Custom metaclass.
    """


@contextlib.contextmanager
def temporary_binding(
    instance_or_class: object, attr: str, new_value: Any
) -> Generator[None, None, None]:
    """
    Temporarily bind a class or instance attribute to a new value within this context
    manager's scope, then restore its original value when exiting the context.
    """
    old_value = getattr(instance_or_class, attr, None)
    try:
        setattr(instance_or_class, attr, new_value)
        yield
    finally:
        if old_value is None:
            delattr(instance_or_class, attr)
        else:
            setattr(instance_or_class, attr, old_value)


class A(metaclass=Meta):
    """A simple class."""

    x: int
    y