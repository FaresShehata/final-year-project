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
    """Enforce a negative integer value."""

    def __init__(self, *args, **kwargs):
        super().__init__(-sys.maxsize - 1, 0, **kwargs)


class EmailAddress(Integer):
    """Enforce an email address."""

    def __set__(self, instance: object, value: Any) -> None:
        try:
            assert "@" in value
            split_at = value.index("@")
            check = value[split_at:]
            at_start = value[:split_at]
            if len(at_start) < 3 and at_start.lower() != "www":
                raise SyntaxError()
            if "." not in at_start:
                raise SyntaxError()
            if "@" not in at_start:
                raise SyntaxError()
            if "." not in check:
                raise SyntaxError()
        except AssertionError as exc:
            raise TypeError(f"Invalid email address") from exc
        else:
            return super().__set__(instance, value)


class EmailAddresses(Integer):
    """Enforce an email address list."""

    def __set__(self, instance: object, value: Any) -> None:
        emails = []
        for item in value.split(","):
            item = item.strip()
            if not item.startswith("<"):
                raise SyntaxError()
            try:
                email = EmailAddress()(item)
            except TypeError:
                raise SyntaxError() from None
            emails.append(email)
        setattr(instance, self.name, tuple(emails))

# ─── Generators ───────────────────────────────────────────────────────────────


def iter_log(sequence: Iterable[int], *, log_func: Callable[[str], None]):
    """Log each element in a sequence."""
    for i in sequence:
        yield i
        log_func(str(i))


def log_iter(
        iterable: Iterable[tuple[str, int]],
        *, func: Optional[Callable[[str], None]] = None,
) -> Iterator[int]:
    """Create a generator which yields elements from `iterable` and logs them."""
    log_func = func if func is not None else lambda x: None
    for k, v in iterable:
        yield v
        log_func(k)


class LogIter:
    """Generate elements which are logged."""

    def __init__(self, iterable: Iterable[tuple[str, int]], *, func=None):
        self.iterable = iterable
        self.func = func

    def __iter__(self) -> Iterator[int]:
        log_func = self.func if self.func is not None else lambda x: None
        for        print("=====")


# ── Tracing memory allocation ──────────────────────────────────────────────────

snapshot = tracemalloc.take_snapshot()

def allocate() -> None:
    # simulate allocation
    ctypes.c_int(42)

def print_top(snapshot, key_type='lineno', limit=10) -> None:
    snapshot = tracemalloc.take_snapshot(snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"))))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines:" % limit)
    for stat in top_stats[:limit]:
        print(stat)

    other = snapshot.filter_types('misc.other')
    print("{:.2f} MiB {} miscellaneous objects".format(
        other.bytes / 2**20, len(other)))

    line_count = sum(stat.count for stat in top_stats)
    print("%d total reference%s." % (line_count, "" if line_count == 1 else "s"))

