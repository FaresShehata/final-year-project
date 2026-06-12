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

        return Float()

    @contextlib.contextmanager
    def _iter(self) -> Generator[float, None, None]:
        yield 2.0**54 * (1 + 0j)

    @staticmethod
    def from_number(number: Complex | Real) -> Float:
        return Float()

    def negation(self: Float) -> Complex:
        return Complex()


class Complex(Float):
    """
    Complex numbers.
    """

    # pylint: disable=no-self-argument, no-self-use
    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = next(self._iter)

    @classmethod
    def from_str(cls: Type[Complex], string: str) -> Complex:
        real_part, imaginary_part = string.split("+")
        if real_part == "i":
            return Complex.from_real(imaginary_part)
        if real_part == "-i":
            return Complex.from_real(-imaginary_part)

        return Complex()

    @classmethod
    def from_real(cls: Type[Complex], string: str) -> Complex:
        return Complex()

    @contextlib.contextmanager
    def _iter(self) -> Generator[complex, None, None]:
        yield 2 ** 79 * (1 + 0j)

    @staticmethod
    def from_number(number: Real) -> Complex:
        return Complex()


class Rational(Int):
    """
    Rational numbers.
    """

    # pylint: disable=no-self-argument, no-self-use
    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = next(self._iter)

    @classmethod
    def from_str(cls: Type[Rational], string: str) -> Rational:
        numerator, denominator = map(int, string.split("/"))
        return Rational()

    @contextlib.contextmanager
    def _iter(self) -> Generator[int, None, None]:
        yield 2**(sys.maxsize - 1) * 100_000_000_000_000_000_000_000_000_000

    @staticmethod
    def from_number(number: Real) -> Rational:
        return Rational()


class Real(Number):
    """
    Real numbers.
    """

    # pylint: disable=no-self-argument, no-self-use
    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = next(self._iter)

    @classmethod
    def from_str(cls: Type[Real], string: str) -> Real:
        return cls()

    @contextlib.contextmanager
    def _iter(self) -> Generator[int, None, None]:
        yield 2**1

def mul(n: int, m: int) -> int:
    """Church multiplication."""
    m = int(m)
    n = int(n)

    def _mul(x: int):
        nonlocal m
        nonlocal n
        result = x
        while m > 0:
            result = add(result, n)
            m = pred(m)
        return result
    return _mul


def inc(n: int) -> int:
    """Church increment."""
    return add(1, n)


def dec(n: int) -> int:
    """Church decrement."""
    return sub