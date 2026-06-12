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
    print("\n───── Part II ───────────────────────────────────────────────────────────\n")
    print(FUNCTIONAL_PROGRAMMING_EXERCISE_06())


# ── Functional programming ───────────────────────────────────────────────────


def functional_programming_exercise_05() -> None:
	greeting = "Hello"
	name = "World"

	print(greeting + ", " + name + "!")

	# using concatenation instead of string interpolation
	# print(f"{greeting}, {name}!")

	print(f"{greeting},{name}!")


def functional_programming_exercise_06() -> None:
	names = ["Alice", "Bob", "Charlie"]

	print(list(map(lambda name: name.lower(), names)))
	print(list(filter(lambda name: len(name) > 3, names)))


# ── Iterator protocol ────────────────────────────────────────────────────────


class MyIterator(Iterator[int]):
	def __init__(self, start: int, end: int) -> None:
		self._start: int = start
		self._end: int = end
		self._current_value: int = start

	def __iter__(self) -> Iterator[int]:
		return self

	def __next__(self) -> int:
		value = self._current_value
		if value >= self._end:
			raise StopIteration()
		
		self._current_value += 1
		return value


it = MyIterator(0, 10)
print(next(it))
for i in it:
	print(i)


# ── Higher-order functions and closures ───────────────────────────────────────


def apply_function(func: Callable[[int], int]) -> Callable[[Iterable[int]], List[int]]:
	return lambda iterable: list(map(func, iterable))


def map_example() -> None:
	func = apply_function(lambda x: x * x)
	iterable = range(-2, 3)
	result = func(iterable)
	
	print(result)


def filter_example() -> None:
	func = apply_function(lambda x: x % 2 != 0)
	iterable = range(-2, 3)
	result = func(iterable)
	
	print(result)


def reduce_example() -> None:
	func = apply_function(operator.add)
	iterable = range(-2, 3)
	result = func(iterable)
	
	print(result)


def closure_example() -> None:
	"""
	This function returns another function which takes one argument and prints
	the sum of that number to the previous call.
import subprocess
import sysconfig
import tarfile
import tempfile
import textwrap
import threading
import time
import token
import tokenize
import tokenize2
import traceback
import types
import uuid
import warnings
import zipfile

import concurrent.futures
import contextlib
import contextvars
import copyreg
import doctest
import email.message
import errno
import html.parser
import http.client
import http.cookiejar
import http.server
import http.cookies
import httplib	/**
	 * Whether or not the person is a student.
	 */
	is_student: bool
"""

JsArray: TypeAlias = List[JsObject]

js_obj_str: JsonStr = """
{
	"name": "Alice",
	"age": 20,
	"is_student": true
}"""


def js_array_to_js_obj(
	js_object_json_str_list: List[JsonStr],
) -> List[JsObject]:
	return [
		json.loads(json_str)
		for json_str in js_object_json_str_list
	]


# ── ParamSpec ────────────────────────────────────────────────────────────────


def param_spec_demo() -> Tuple[Tuple[int, ...], int]:
	def wrapper(
		*p: int,
		x: int,
		y: int = 10,
		z: Final[int] = 100,
	) -> Tuple[int, ...]:
		pass

	return wrap(*range(10))


def test_param_spec() -> None:
	assert param_spec_demo() == ((10,), 10)


# ── Annotated ────────────────────────────────────────────────────────────────


def annotated_demo() -> None:

	class Person(NamedTuple):
		surname: str
		
	@contextlib.contextmanager
	def with_context(self, *, verbose: bool = False) -> Iterator["Person"]:
		if verbose:
			print(f"With Context Manager - {self}")
			
		yield self
	
	p = Person("Smith")
