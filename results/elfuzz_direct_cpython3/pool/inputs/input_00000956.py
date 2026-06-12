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
AND   = lambda x: lambda y: x(y)(x)
OR    = lambda x: lambda y: x(x)(y)

# ─── Higher-order functions ─────────────────────────────────────────────────


def add(a: int) -> Callable[[int], int]:
    return lambda b: a + b


def double(a: A) -> A:
    return a * 2


# ─────────────────────────────────────────────────────────────────────────────


def is_even(n: int) -> bool:
    return n % 2 == 0


# ─── Comprehension / generator expressions ────────────────────────────────────


class xrange:

    def __init__(self, start=0, end=sys.maxsize):
        self.i = start - 1

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.i >= end:
            raise StopIteration
        self.i += 1
        return self.i


def infinite_xrange(start=0):
    while True:
        yield start
        start += 1


def natural_numbers() -> Generator[int, None, None]:
    for i in itertools.count(1):
        yield i


def evens() -> Generator[int, None, None]:
    i = 0
    while True:
        i += 2
        yield i


# ─── Infinite streams of values ───────────────────────────────────────────────


def stream(func: Callable[[], int]) -> Iterable[int]:
    """Generates values from function func."""
    while True:
        value = func()
        yield value


@functools.cache
def fib(n: int) -> int:
    """
    Calculates the nth Fibonacci number using only the first two numbers.
    """

    # Base case: F(0) = 0 and F(1) = 1
    if n <= 1:
        return n

    # Recursive case: F(n) = F(n-1) + F(n-2)
    else:
        return fib(n - 1) + fib(n - 2)


def fibonacci_stream():
    """
    Generates Fibonacci numbers.
    """
    # Start with the first two Fibonacci numbers, F(0) = 0 and F(1) = 1
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def gen_fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def lazy_seq(iterable):
    return map(next, iterable)


# ─────────────────────────────────────────────────────────────────────────────


def repeat_once(generator: Generator[A, None, None] | Iterable[A]):
    try:
        next(generator)
    except StopIteration:
        pass


def repeat_many_times(
    ntimes: int, generator: Generator[A, None, None] | Iterable[A]
):
    for _ in range(ntimes):
        repeat_once(generator)


# ─── Closures, decorators and generators ──────────────────────────────────────


def make_adder(n: int):
    """
    Returns a closure that adds `n` to its argument.

    This function takes an integer `n` as input and returns a closure. The returned closure can be used to perform addition by adding `n` to any given argument.

    Args:
      n (int): An integer representing the number to be added to the result.

    Returns:
      closure: A closure that takes an argument and returns the sum of `n` and the argument.

    Example usage:
    >>> add_three = make_adder(3)
    >>> add_three(10)
    13
    """

    def adder(value: int) -> int:
        return n + value

    return adder


def memoize(func: Callable[..., B]) -> Callable[..., B]:
    cache: dict[tuple[Any, ...], B] = {}

    @functools.wraps(func)
    def inner(*args: Any, **kwargs: Any) -> B:
        key = tuple((*args, *sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return inner


def countdown(i: int) -> Generator[int, None, None]:
    """
    Counts down from a given integer.

    This function accepts an integer 'i' as input and generates a sequence of integers counting down from 'i'.

    Args:
      i (int): An integer representing the initial count from which the countdown will begin.

    Yields:
      int: Each integer in the countdown sequence, starting from 'i' and decrementing until it reaches 0        code.co_varnames,
        code.co_filename,
        code.co_name,
        code.co_firstlineno,
        code.co_lnotab,
        code.co_freevars,
        code.co_cellvars,
    )
    return annotated_disassembly(code_obj)


# ── Low-level types and operations ────────────────────────────────────────────

def test_ctypes():
    return ctypes.c_int32(789456123) == ctypes.c_ulonglong(789456123)

def test_struct():
    x = array.array('i', [789456123])
    print(x.itemsize)
    
    return struct.unpack('>I', b'\x7\x8\x9\x4\x5\x6\x1\x2')[0]

def test_pickle():
    x = array.array('i', [789456123])

    data = pickle.dumps(x)
    print(pretty_marshal(data))

    y = pickle.loads(data)
    assert x.tolist() == y.tolist()

    z = bytearray([1, 2, 3])
    data = pickle.dumps(z)
    w = pickle.loads(data)
    assert list(w) == [1, 2, 3]


# ── Memoryview utilities ──────────────────────────────────────────────────────

def test_memoryview():
    x = array.array('u')
    x.frombytes(b"Hello world!\0")
    mv = memoryview(x)
    mv[1::2].readonly = True
    assert mv.readonly is True


# ── Pickle tools utility functions ────────────────────────────────────────────

def show_opcode_table(opcodes=None):
    """
    Display opcode table.
    """
   