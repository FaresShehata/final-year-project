"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
PRED  = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda u: x)(lambda u: u)
DEC   = lambda n: PRED(PRED(PRED(PRED(n))))

SINH  = lambda x: ADD(2 * x ** 2 - 1, MUL(x, SINH(x))) / 2
COSH  = lambda x: ADD(MUL(2, Cosh(x)), ONE) / 4
TANH  = lambda x: DIV(SINH(x), COSH(x))

ONE   = lambda x: 1
PLUS  = lambda a: lambda b: lambda c: SUM(a(b))(c)
SUM   = lambda f: lambda x: lambda y: x(y)(f)
MULT  = lambda a: lambda b: MULTIPLY(a)(b) if not isinstance(b, int) else lambda c: PRODUCT(a)(c)
PRODUCT = lambda a: lambda b: lambda c: a(b)(c)(a)
DIVIDE = lambda a: lambda b: lambda c: SUBTRACT(a(c))(b)
SUBTRACT = lambda a: lambda b: lambda c: MULTIPLY(a)(b)(c)


def main():
    print("\n───── Part I ───────────────────────────────────────────────────────────\n")
    print(FUNCTIONAL_PROGRAMMING_EXERCISE_05())

    # ──────────────────────────────────────────────────────────────────────────


def FUNCTIONAL_PROGRAMMING_EXERCISE_01() -> str:
    """
    Exercise 1.

    Create a function that will take an argument and return the square of it.
    """

    def square_number(num):
        pass

    return square_number


def FUNCTIONAL_PROGRAMMING_EXERCISE_02(arg: A) -> B:
    """
    Exercise 2.

    Create a function that will take two arguments and return their sum.
    """

    def add_numbers(a, b):
        pass

    return add_numbers


def FUNCTIONAL_PROGRAMMING_EXERCISE_03() -> bool:
    """
    Exercise 3.

    Create a function that will take one argument and return its negation.
    """

    def negate(value):
        pass

    return negate


def FUNCTIONAL_PROGRAMMING_EXERCISE_04(*args: A) -> B:
    """
    Exercise 4.

    Create a function that will take any number of arguments and return their product.
    """

    def multiply_args(*args):
        pass

    return multiply_args


def FUNCTIONAL_PROGRAMMING_EXERCISE_05():
    """
    Exercise 5.

    Implement the following functions using only recursion:

    - factorial
    - fibonacci
    - sum_of_digits
    """

    def factorial(number: int) -> int:
        """
        Factorial implementation via recursion.
        :param number: The number to compute the factorial for.
        :return: The factorial value.
        """

        def _factorial(n):
            if n == 1 or n == 0:
                return 1
            return n * _factorial(n-1)

        return _factorial(number)

    def fibonacci(n: int) -> int:
        """
        Fibonacci sequence generator via recursion.
        :param n: Index of the Fibonacci number in the sequence.
        :return: The requested Fibonacci number.
        """

        def _fibonacci(n):
            if n <= 1:
                return n
            return _fibonacci(n - 1) + _fibonacci(n - 2)

        return _fibonacci(n)

    def sum_of_digits(number: int) -> int:
        """
        Sum up all digits of an integer recursively.
        :param number: Integer number whose digits you want to sum up.
        :return: Sum of all digits.
        """

        def _sum_digits(digits: list[int]) -> int:
            if len(digits) == 1:
                return digits[0]
            return digits[-1] + _sum_digits(digits[:-1])

        return _sum_digits([int(digit) for digit in str(abs(number))])

    return {
        "factorial": factorial,
        "fibonacci": fibonacci,
        "sum_of_digits": sum_of_digits,
    }


def FUNCTIONAL_PROGRAMMING_EXERCISE_06() -> tuple[int, int]:
    """
