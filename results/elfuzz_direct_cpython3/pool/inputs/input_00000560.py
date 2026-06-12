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
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # If the method is called with an instance, this will be None because
        # we have set `obj=None` in the constructor.
        cache = obj._cache
        if self.attrname:
            cache = cache.setdefault(self.attrname, {})
        result = cache.get(self)
        if result is None:
            result = cache[self] = self.func(obj)
        return result


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.cnt += 1
        print(wrapper.cnt, ":", end=" ")
        return func(*args, **kwargs)

    wrapper.cnt = 0
    return wrapper


@count_calls
def factorial(n: int) -> int:
    """Calculate n! (factorial of n)."""

    if n < 0 or not isinstance(n, int):
        raise ValueError("n must be a non-negative integer.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print(factorial(5))
print(factorial.cnt)

# ── Protocol classes ─────────────────────────────────────────────────────────

class Comparable(metaclass=abc.ABCMeta):
    """ABC defining a protocol class used for equality comparison."""

    @classmethod
    @abc.abstractmethod
    def parse(cls, arg: str) -> Comparable:
        pass

    @abc.abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abc.abstractmethod
    def __lt__(self, other) -> bool:
        pass

    @classmethod
    def parse_list(cls, args: list[str]) -> list[Comparable]:
        return [cls.parse(arg) for arg in args]

    def __repr__(self) -> str:
        return f"<{self}>"

    def __hash__(self) -> int:
        return hash(repr(self))

    def __le__(self, other) -> bool:
        return self == other or self < other

    @classmethod
    def make_comparable(cls) -> type[Comparable]:
        """Use this decorator on a custom class to add methods required by the Comparable protocol."""
        cls.parse = staticmethod(cls.parse)
        cls.__lt__ = cls.__le__
        cls.__ge__ = lambda self, other: not self < other
        cls.__gt__ = lambda self, other: not self <= other
        cls.__ne__ = lambda self, other: not self == other
        return cls


class Money:
    """Class representing monetary amounts.

    Implements the Protocol defined by 'Comparable'.
    """

    money: float

    def __init__(self, money: float) -> None:
        self.money = money

    @classmethod
    def parse(cls, arg: str) -> Money:
        match arg.split():
            case ["$", amount]:
                return Money(float(amount[1:]))
            case ["£", amount]:
                return Money(float(amount[1:]))
            case ["€", amount]:
                return Money(float(amount[1:]))
            case []:
                raise ValueError()
            case _:
                raise ValueError()

    def __eq__(self, other) -> bool:
        try:
            return abs(self.money - other.money) < 0.00001
        except AttributeError:
            return False

    def __lt__(self, other) -> bool:
        return self.money < other.money


@make_comparable()
class Vector:
    x: int
    y: int

    def __    except Exception as ex:
        print(f"Invalid expression '{expr}': {ex}", file=sys.stderr)
        exit(-1)


# ── Comprehensions & generator functions ──────────────────────────────────────

def primes_up_to(max_: int) -> Generator[int, None, None]:
    """Generate primes up to max_ using trial division."""
    yield from filter(is_prime, range(2, max_))


def is_prime(n: int) -> bool:
    """Test whether n is prime by trial division."""
    return all(n % d != 0 for d in range(2, n))


def fibonacci_up_to(max_: int) -> Iterator[int]:
    """Yield Fibonacci numbers less than max_, using generator expressions and yields."""
    a, b = 0, 1
    while True:
        if a < max_:
            yield a
        else:
            break
        a, b = b, a + b


def fibonacci_list(max_: int) -> list[int]:
    """Yield Fibonacci numbers less than max_, using list comprehensions and returns."""
    return [a for a, _ in zip(itertools.count(), fibonacci_up_to(max_))]


def fibonacci_dict(max_: int) -> dict[int, int]:
    """Yield Fibonacci numbers less than max_, using dictionary comprehensions and returns."""
    return {i: a for i, a, *_ in enumerate(itertools.zip_longest(*[fibonacci_up_to(max_), *[None]*9]))}


def fibonacci_generator(max_: int) -> Generator[int, None, None]:
    """Yield Fibonacci numbers less than max_, using generator expressions and yields."""
    return (a for a, _ in zip(itertools.count(), fibonacci_up_to(max_)))


def fibonacci_lists(max_: int) -> tuple[list[int], ...]:
    """Yield lists of Fibonacci numbers less than max_, using list comprehensions and yields."""
    return (
        list(zip(itertools.count(), fibonacci_up_to(max_))),
        list(map(operator.itemgetter(0), fibonacci_up_to(max_))),
        list(map(operator.itemgetter(1), fibonacci_updef count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


