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


class Descriptor:
    """A simple descriptor."""

    def __init__(self) -> None:
        self._value: str | int = ""

    @property
    def value(self) -> str | int:
        return self._value

    @value.setter
    def value(self, val: str | int) -> None:
        self._value = val

    def __get__(self, instance: object | None, owner: type) -> str | int:
        return self.value

    def __set__(self, instance: object | None, val: str | int) -> None:
        # Note that the code below is equivalent to `instance.__dict__["_value"]`.
        if not isinstance(val, (str, int)):
            raise TypeError(f"Expected {type(val).__name__}, got {type(val)}!")

        self.value = val


class AgeDescriptor(Descriptor):
    """An age descriptor."""

    def __get__(self, instance: object | None, owner: type) -> int:
        try:
            return super().__get__(instance)
        except AttributeError as err:
            raise RuntimeError(
                "Age must be set on a Person before it can be accessed!"
            ) from err

    def __set__(self, instance: object | None, val: int) -> None:
        if val < 0:
            raise ValueError(f"Invalid age: {val}!")
        super().__set__(instance, val)


class FullnameDescriptor(Descriptor):
    """A fullname descriptor."""

    def __get__(self, instance: Person | None, owner: type) -> str | None:
        try:
            return super().__get__(instance)
        except AttributeError as err:
            raise RuntimeError(
                "Full name must be set on a Person before it can be accessed!"
            ) from err


class Person:
    """A class with data attributes and methods."""

    _age_descriptor = AgeDescriptor()
    _fullname_descriptor = FullnameDescriptor()

    def __init__(self, full_name: str, age: int) -> None:
        self.full_name = full_name
        self.age = age

    @classmethod
    def create(cls, *args, **kwargs) -> Person:
        person = cls(*args, **kwargs)
        person._age_descriptor.value += 1
        return person

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(full_name={