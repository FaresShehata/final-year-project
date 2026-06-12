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
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


add4 = curry(add3)


# ── Partial application example - adding arguments to the right ─────────────

def add_right(a: int) -> Callable[[int], int]:
    """Adds an argument to the right of a partially applied function.""" 
    return lambda b: add3(b, a)


def add_left(a: int) -> Callable[[int], int]:
    """Adds an argument to the left of a partially applied function."""
    return lambda b: add3(a, b)


two_plus = add_right(2)
three_times = add_left(3)


# ── Higher order functions example - sorting with key and reverse ────────────

students = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "Charlie", "age": 28},
]

sorted_students_by_age = sorted(students, key=lambda student: student["age"])
sorted_students_by_name_reverse = sorted(
    students, key=lambda student: student["name"], reverse=True
)


# ── Generators and iterators example - Fibonacci numbers ─────────────────────

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib_gen = fibonacci()
print(next(fib_gen))  # 0
print(next(fib_gen))  # 1
print(next(fib_gen))  # 1
print(next(fib_gen))  # 2
print(next(fib_gen))  # 3

# ── Coroutines example - lazy list generator ─────────────────────────────────

def lazy_list_generator():
    i = 0
    while True:
        try:
            value = yield i
            i += 1
            print(value, i)
        except ValueError as e:
            print(e.args[0])

gen = lazy_list_generator()
next(gen)  # Start the coroutine
for i in [9, 7, "foo"]:
    gen.send(i)  # Send values to the coroutine

# ── Trampoline example - optimizing recursive Fibonacci calculation ─────────

def fib_trampoline(n):
    def fib_recursive(index=0, current=0, next=1):
        nonlocal index
        index += 1
       