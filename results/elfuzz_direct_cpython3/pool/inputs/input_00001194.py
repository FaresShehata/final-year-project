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

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)" if hasattr(self, "lo") else ""
            )
        elif (getattr(obj, self.name) is not None or self.lo is None) and (
            getattr(obj, self.name)
            + getattr(obj, self.lo) >= val
            if self.lo is not None and val > self.lo
            else True
        ):
            raise ValueError(f"{self.name} must be less than {self.lo}")
        elif (getattr(obj, self.name) is not None or self.hi is None) and (
            getattr(obj, self.name)
            - getattr(obj, self.hi) <= val
            if self.hi is not None and val < self.hi
            else True
        ):
            raise ValueError(f"{self.name} must be greater than {self.hi}")
        setattr(obj, self.name, val)


class PositiveFloat(TypedDescriptor):
    def __set__(self, obj, value):
        try:
            return super().__set__(obj, float(value))
        except Exception as e:
            raise e


class PositiveInt(TypedDescriptor):
    def __set__(self, obj, value):
        try:
            return super().__set__(obj, int(value))
        except Exception as e:
            raise e


# ── Metaclasses ───────────────────────────────────────────────────────────────

class Meta(type):
    """A simple example of a metaclass for the purpose of learning how they work."""

    @classmethod
    def __prepare__(metacls, cls, bases):
        print(f"Prepare: {bases=}\n")
        return vars()

    def __new__(metacls, cls, bases, namespace):
        print(f"\nNew: {namespace=}\n")
        return super().__new__(metacls, cls, bases, namespace)

    def __init__(cls, class_name, bases, namespace):
        print(f"Init: {dict(cls.__dict__)=}\n")
        return super().__init__(class_name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        print(f"Call:")
        instance = super().__call__(*args, **kwargs)
        print(dict(instance.__dict__))
        return instance


# ── Classes ───────────────────────────────────────────────────────────────────

class Animal(metaclass=Meta):
    """Base class for all animals in our zoo.

    Provides generic behaviour across all animals.
    """

    #