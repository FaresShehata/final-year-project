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

@functools.partial(operator.add, 2)
def add_two(x):
    print(f"add_two({x}) returns: {x+2}")

@functools.partial(operator.mul, 2)
def multiply_by_2(x):
    print(f"multiply_by_2({x}) returns: {x*2}")


# ── Trampoline example ───────────────────────────────────────────────────────

class AsyncIterator:
    """Async iterator base class."""
    
    def __init__(self):
        self._iters: list[Generator[Any, None, None]] = []
    
    @property
    def iterable(self) -> bool:
        """
        Return `True` if the underlying object is an instance of a generator.
        This will be useful to know when waiting on asynchronous operations.
        """
        try:
            return next(iter(self)).isinstance(Generator)
        except StopIteration:
            return False
    
    def __iter__(self) -> Iterator[Any]:
        return iter(self._iters)
    
    def send(self, value: Any) -> Any:
        """
        Send data into the async iterator's underlying generators and get their
        results back as a new generator.
        
        :param value: Data sent to the generator.
        :return: Result yielded by each generator.
        """
        while not all(map(generator_send, self._iters, [value])):
            yield from self.send(value)
        return self.get_result()
    
    
    def throw(self, exc_type: type[BaseException], exc_value: BaseException | None = None, traceback: TracebackType | None = None) -> Any:
        """
        Raise an exception within the underlying generators.
        
        :param exc_type: The exception type.
        :param exc_value: The exception value.
        :param traceback: The exception traceback.
        :raise RuntimeError: If this method is called more than once.
        """
        raise RuntimeError('Can\'t call "throw()" after calling "close()"')
        
    def close(self) -> None:
        """
        Close the underlying generators, sending them their own closing messages.
        """
        self.throw(BaseException())
    

    def get_result(self) -> Any:
        """
        Get the last result yielded by the underlying generators.
        """
        try:
            return next(iter(self)).result
        except StopIteration as e:
            return e.value
    

    def add_iter(self, iters: Iterable