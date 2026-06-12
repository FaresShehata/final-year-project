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

    def conjugate(self: Complex) -> Complex:
        if isinstance(self.value, complex):
            self.value += 0j
        else:
            self.value *= complex(0, 1)
        return self

    def exp(self: Complex) -> Complex:
        self.value *= complex(math.e, 0)
        return self

    def log(self: Complex) -> Complex:
        self.value /= math.e ** (-complex(0, 1))
        return self

    def sqrt(self: Complex) -> Complex:
        base = complex(abs(self), 0).sqrt()
        if self.real < 0 and self.imag > 0:
            base *= -1
        elif self.real < 0 and self.imag < 0:
            base = -base
        self.value = base
        return self


class Real(Number):
    """
    Real numbers.
    """

    __slots__ = ["value"]

    def __init__(self) -> None:
        self.value = next(self._iter)


class Rational(Real):
    """
    Rational numbers.
    """

    # pylint: disable=no-self-argument, no-self-use
    __slots__ = ["numerator", "denominator"]

    numerator: int
    denominator: int

    def __init__(self) -> None:
        pass

    @classmethod
    def from_str(cls: Type[Rational], string: str) -> Rational:
        tokens = string.split("/")
        if len(tokens) != 2 or not all(token.isdigit() for token in tokens[:2]):
            raise ValueError(f"{string} is not a rational number.")
        return Rational()

    @classmethod
    def from_real(cls: Type[Rational], real: Real) -> Rational:
        return Rational()

    @classmethod
    def from_float(cls: Type[Rational], flt: Float | Complex) -> Rational:
        return Rational()


@functools.total_ordering
class Complex(Real):
    """
    Complex numbers.
    """

    __slots__: list[str] = ["real", "imaginary"]
