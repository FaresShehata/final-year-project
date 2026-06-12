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
        self.name = name
        if issubclass(self.expected_type, Integer):
            self.low = self.lo or -sys.maxsize
            self.high = self.hi or sys.maxsize

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if name == "":
            raise ValueError(f"{name} must be non-empty string")
        elif not isinstance(name, str):
            raise TypeError(f"{name} must be {str.__name__}")
        elif not any(map(str.isalpha, name)):
            raise TypeError(f"{name} must contain only letters")
        elif len(set(name)) > len(name):
            raise TypeError(f"{name} contains duplicate characters")
        self._name = name

    def __get__(self, instance: T, owner: type) -> Any:
        return getattr(instance, f"_Typed{self.name}")

    def __set__(self, instance: T, value: Any) -> None:
        # Check if value is of the right type.
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{value} must have type {self.expected_type.__name__}")
        elif (
            self.low is not None
            and self.high is not None
            and not (self.low <= value <= self.high)
        ):
            msg = {
                self.low,
                self.high,
            } = (
                (self.low, value),
                (value, self.high),
            )
            raise TypeError(
                f"{msg[1]} must fall between {msg[0]} and {self.high}"
            )

        setattr(instance, f"_Typed{self.name}", value)

    def __delete__(self, instance: T) -> None:
        delattr(instance, f"_Typed{self.name}")


class Integer(TypedDescriptor):
    """An integer descriptor."""


class Float(TypedDescriptor):
    """A float descriptor."""


class String(TypedDescriptor):
    """A string descriptor."""


class Boolean(TypedDescriptor):
    """A boolean descriptor."""


class LowercaseString(String):
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    """Enforce an email address."""

    def __set__(self, instance: object, value: Any) -> None:
        try:
            assert "@" in value
            split_at = value.index("@")
            check = value[split_at:]
            at_start = value[:split_at]
            if len(at_start) < 3 and at_start.lower() != "www":
                raise SyntaxError()
            if "." not in at_start:
                raise SyntaxError()
            if "@" not in at_start:
                raise SyntaxError()
            if "." not in check:
                raise SyntaxError()
        except AssertionError as exc:
            raise TypeError(f"Invalid email address") from exc
        else:
            return super().__set__(instance, value)


class EmailAddresses(Integer):
    """Enforce an email address list."""

    def __set__(self, instance: object, value: Any) -> None:
        emails = []
        for item in value.split(","):
