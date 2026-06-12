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
    """A descriptor that is used to control the type of an attribute."""

    @classmethod
    def check_type(cls: Type[T], value: T) -> None:
        if not isinstance(value, cls._type):
            raise TypeError(f"Expected {cls._type.__name__}.")

    _type: type

    def __init__(self: TypedDescriptor, name: str) -> None:
        self.name = name

    def __set_name__(self: TypedDescriptor, owner: type, name: str) -> None:
        self.name = name
        setattr(owner, f"_original_{name}", property(self.get))

    def get(self: TypedDescriptor, instance: object) -> Any:
        return getattr(instance, f"_original_{self.name}")

    def set(self: TypedDescriptor, instance: object, value: Any) -> None:
        self.check_type(value)
        setattr(instance, f"_original_{self.name}", value)


class TypedInstanceVariable(TypedDescriptor):

    def __get__(self: TypedDescriptor, obj: object, cls: type) -> Any:
        if obj is None:
            return self
        return super().__get__(obj)

    def __set__(self: TypedDescriptor, obj: object, value: Any) -> None:
        super().__set__(obj, value)


# ── Metaclasses ──────────────────────────────────────────────────────────────

def describe_metaclass(
    meta: type,
    *,
    indent: int = 2,
    depth: int = 5,
) -> str:

    def _describe(metaclass: type) -> str:

        class_ = metaclass.__bases__[0]
        bases = ", ".join(_describe(b) for b in class_.__mro__)
        bases = f"{bases[:-2]}." if bases.endswith(".") else bases
        result = (
            " " * indent +
            f"{metaclass.__module__}.{metaclass.__qualname__}"
            f"(base={bases})"
        )
        return result + "\n" if depth > 0 else ""

    result = ""
    if hasattr(meta, "__orig_bases__"):
        mro = meta.mro()
        base_class = mro[mro.index(meta) - 1]
        result += _describe(base_class)
        result += _describe(meta)
    elif meta != type:
        result += _describe(type)
    elif hasattr(sys, "_getframe") and len(sys._get    num = 0
    while True:
        yield num
        num += 1
