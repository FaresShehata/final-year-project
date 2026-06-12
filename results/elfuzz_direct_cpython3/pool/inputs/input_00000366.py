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


class Meta(type):
    """
    Meta class for the example classes.
    """

    def __init__(cls: type[T], name: str, bases: tuple[type[Any]], attrs: dict[str, Any]) -> None:
        super().__init__(name, bases, attrs)
        cls.__repr__ = lambda self_: f"<{self_.value}>"


class Number(metaclass=Meta):
    """
    Base number.
    """

    __slots__: list[str] = []

    value: int

    def __init__(self) -> None:
        ...

    @classmethod
    def from_str(cls: Type[Number], string: str) -> Number:
        return cls()


class Int(Number):
    """
    Integer numbers.
    """

    # pylint: disable=no-self-argument, no-self-use
    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = next(self._iter)

    @contextlib.contextmanager
    def _iter(self) -> Generator[int, None, None]:
        yield 2**63 - 1

    @staticmethod
    def from_str(string: str) -> Int:
        return Int()

    def negate(self: Int) -> Int:
        return Int.from_str("-" + str(self.value))


class Float(Number):
    """
    Floating point numbers.
    """

    # pylint: disable=no-self-argument, no-self-use
    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = next(self._iter)

    @classmethod
    def from_str(cls: Type[Float], string: str) -> Float:
        if len(string.split(".")) != 2:
            raise ValueError(f"{string} is not a float.")
        integer_part, decimal_part = string.split(".")
        if integer_part == "inf":
            return Float.from_str("+inf")
        if integer_part == "-inf":
            return Float.from_str("-inf")
        if decimal_part == "nan":
            return Float.from_str("nan")

        try:
            return Float()
        except OverflowError as exc:
            raise ValueError(f"{string} is too large.") from exc

    @contextlib.contextmanager
    def _iter(self) -> Generator[float, None, None]:
        yield 1.7976931348623157e+308