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

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __set__(self, instance: object, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {type(self).__name__} got {value}")
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name} must be >= {repr(self.lo)}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name} must be <= {repr(self.hi)}")
        setattr(instance, self.name, value)

    def __get__(self, instance: object, cls: Type[T]) -> TypedDescriptor:
        return self


class Integer(TypedDescriptor):
    """
    Enforce an integer value.
    Optionally constrain to a lower and/or upper bound.
    """

    def __set__(self, instance: object, value: Any) -> None:
        super().__set__(instance, int(value))


class Range(Integer):
    """Enforce the bounds of a numeric value."""

    def __init__(
        self,
        low: int,
        high: int,
        *,
        inclusive: bool = False,
        **kwargs,
    ):
        super().__init__(int, **kwargs)
        self.low = low
        self.high = high
        self.inclusive = inclusive

    def __set__(self, instance: object, value: Any) -> None:
        super().__set__(instance, int(value))
        if (
                (not self.inclusive or value != self.high)
                and value > self.high
        ):
            raise ValueError(
                f"{self.name} must be between "
                f"{repr(self.low)} and {repr(self.high)}"
            )
        if (
                (not self.inclusive or value != self.low)
                and value < self.low
        ):
            raise ValueError(
                f"{self.name} must be between "
                f"{repr(self.low)} and {repr(self.high)}"
            )


class Positive(Range):
    """Enforce a positive integer value.

    Note that this does not prevent negative integers from being cast into
    positives; it only prevents them from being assigned directly to the
    attribute.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(0, sys.maxsize, inclusive=True, *args, **kwargs)


class Negative(Range):
    """Enforce a negative integer value.

    Note that    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_adder(n: int):
    def adder(m: int) -> int:
        return n + m
    return adder


def memoize(func: Callable) -> Callable:
    cache = WeakKeyDictionary()

    @functools.wraps(func)
    def wrapped(obj: T, *args, **kwargs) -> Any:
        key = func, args, frozenset(kwargs.items())

        if obj not in cache:
            cache[obj] = func(obj, *args, **kwargs)

        return cache[obj]

    return wrapped


# ── Generators ────────────────────────────────────────────────────────────────

class CounterGens:
    """A counter generator class."""

    def __init__(self, initial=0, step=1):
        self.initial = initial
        self.step = step

    def __iter__(self) -> Iterator[int]:
        current = self.initial
        while True:
            yield current
            current += self.step


def countdown_generator(max_count: int = 5, *, start=0) -> Generator[int, None, None]:
    """Yield values counting down from max_count starting at start."""
    end = start + max_count
    for i in range(start, end):
        yield i


def count_up_to(end: int, *, start=0) -> Generator[int, None, None]:
    """Generate numbers up through end, starting at start."""
    for num in range(start, end + 1):
        yield num


def count_down_from(start: int, *, end=0) -> Generator[int, None, None]:
    """Generate numbers down from start, ending at end."""
    for num in range(start, end - 1, -1):
        yield num


def take(count: int, iterable: Iterable) -> Generator:
    """Take items from the front of an iterator."""
    counter, stored = itertools.tee(iterable)
    for _ in range(count):
        if counter:
            yield next(stored)
        else:
            raise StopIteration


def distinct(iterable: Iterable) -> Generator:
    """Return unique items by eliminating duplicates."""
    seen = set()
    for item in iterable:
        if item in seen:
            continue
        yield item
        seen.add(item)


def ordered(iterable: Iterable, *, reverse=False) -> Generator:
    """Return an iterator of the elements in iterable sorted by their natural order."""
    iterable = tuple(iterawait trampoline_maker(coro)


class TrampolineError(Exception):
    pass


async def trampoline(coroutine: Coroutine[Any, Any, Any]) -> Any:
    """Run a coroutine until completion or a StopAsyncIteration exception."""
    assert await coroutine.send(TRAMPOLINE_MAGIC) == TRAMPOLINE_MAGIC
    while True:
        try:
            next_value = await coroutine.send(await coroutine.send())
        except TrampolineError as exc:
            raise exc.args[0] from None
        except StopAsyncIteration as stop:
            return stop.args[0]


@trampoline_maker(generator_yielder(0))


# ── Class and metaclass inheritance ─def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


