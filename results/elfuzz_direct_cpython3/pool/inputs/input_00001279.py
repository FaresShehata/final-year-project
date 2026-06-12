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
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar, Union

if sys.version_info >= (3, 9):
    from collections.abc import Callable as _Callable
else:
    from collections.abc import Callable
    _Callable = Callable

from math import sqrt

from dataclasses import dataclass, field
from fractions import Fraction

# ─── TYPES ────────────────────────────────────────────────────────────────

A = TypeVar("A")
B = TypeVar("B")


# ─── ALGEBRAIC DATA TYPE ──────────────────────────────────────────────────

MUTABLE_SET   = set()
CONCRETE_SET  = frozenset()

class Number(MutableSet):

    @property
    def value(self):
        raise NotImplementedError()


class Positive(Number):

    pass


class Integer(Number):

    pass


class Natural(Integer):

    pass


class Rational(Number):

    pass


class Complex(Number):

    pass


class Real(Number):

    pass


class Imaginary(Real):

    pass


class Decimal(Imaginary):

    pass


class Float(Rational):

    pass


class Rationals:

    def __init__(self, numerator: int, denominator: int):
        self.numerator = numerator
        self.denominator = denominator

    def __add__(self, other: Rationals):
        return Rationals(
            self.numerator * other.denominator +
            other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __sub__(self, other: Rationals):
        return Rationals(
            self.numerator * other.denominator -
            other.numerator * self.denominator,
            self.denominator * other.denominator,
        )


    def __truediv__(self, other: Rationals):
        return Rationals(
            self.numerator * other.denominator,
            self.denominator * other.numerator,
        )


    def __eq__(self, other: Rationals):
        return self.value == other.value


    def __lt__(self, other: Rationals):
        return self.value < other.value


    def __le__(self, other: Rationals):
        return self.value <= other.value



# ─── BASIC ALGEBRAIC STRUCTURES ─────────────────────────────────────────────────

ZERO      = Lambda(lambda x: ZERO)
UNIT      = Lambda(lambda x: UNIT)
IDENTITY  = Lambda(lambda x: IDENTITY)
ADD       = lambda m: lambda n:MOD   = lambda m: lambda n: n(DIV(m)(n))(ZERO)
POWER = lambda m: lambda n: MUL(n)(m)
FACT  = lambda n: IF(GT(n)(ZERO))(
    LAMBDA() (
        MULT(n)(FACT(subtract(n)(ONE)))
    )
)(
    ONE
)

λ     = lambda x: lambda y: x(y)


def compose(*args):
    """Compose a list of unary functions."""
    if not args or len(args) == 1:
        return args[0]
    else:
        return lambda x: reduce(operator.__mul__, args[::-1])(x)


def curry(f: Callable[[A], B]) -> Callable[[A], Callable[[A], B]]:
    """
    Curry is a technique to convert a function with multiple arguments into
    a chain of unary functions.
    """

    return lambda x: lambda xs: [x] + xs


@functools.partial(curry, ZERO)
def multiply(a, acc):
    return acc + a


@curry
def add(x: A, ys: List[A]):
    return sum(ys) + x


@curry
def subtract(x: A, ys: List[A]):
    return sum(ys) - x


@curry
def divide(x: A, ys: List[A]):
    return sum(ys) / x


@curry
def power(base: A, exp: int):
    return base**exp


@curry
def mod(base: A, exp: int):
    return base % exp


def factorial():
    return COMPOSE(power(5))(fact)


COMPOSE = compose(
    FACTORIAL,
    POWER,
    MOD,
    DIV,
    POWER,
    SUBTRACT,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
    POWER,
    DIV,
    FACTORIAL,
    ADD,
    FACTORIAL,
    FACTORIAL,
    FACTORIAL,
<|file_sep|>/seed_02.py
"""
Seed 05 — Generative programming using the yield keyword and comprehension syntax
"""

from __future__ import annotations

import copy
import random
import string
import typing as t

import numpy as np
import pandas as pd
from scipy.special import factorial
from sklearn.datasets import make_blobs


def generate_random_string(length: int) -> str:
    """Generate a random string of length `length`."""

    characters = string.ascii_lowercase
    return "".join(random.choice(characters) for _ in range(length))


def generate_random_number(low: float, high: float) -> float:
    """Generate a random number between low and high."""

    return round(random.uniform(low=low, high=high), 4)


def generate_random_array(size: tuple[int, ...], shape: tuple[int, ...]) -> np.ndarray:
    """Generate an array filled with random numbers."""

    return np.random.rand(*size).reshape(shape).tolist()


def generate_random_matrix(rows: int, cols: int) -> np.ndarray:
    """Generate a matrix filled with random numbers."""

    return np.random.randint(0, 256, size=(rows, cols)).astype(np.uint8)


def generate_random_vector(vector_size: int) -> np.ndarray:
    """Generate a vector filled with random numbers."""

    return np.arange(vector_size).reshape((vector_size, 1)).tolist()


def generate_random_integers(count: int, min_val: int, max_val: int) -> list[int]:
    """Generate a list of `count` integers between `min_val` and `max_val`."""

    return sorted([random.randrange(min_val, max_val) for _ in range(count)])



def generate_random_floats(count: int, min_val: float, max_val: float) -> list[float]:
    """Generate a list of `count` floats between `min_val` and `max_val`."""

    return sorted(list(map(round, [generate_random_number(min_val, max_val) for _ in range(count)])))


def generate_random_strings(count: int, size: int) -> list[str]:
    """Generate a list of `count` strings each of length `size`."""

    return sorted([generate_random_string(size) for _ in range(count)])


    FACTORIAL,
)

