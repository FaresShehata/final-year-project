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

    def __set__(self, obj, val):
        if not isinstance(val, self.expected_type):
            raise TypeError(
                f"Expected {self.expected_type}, got {val!r}"
                "(expected type)"
            )
        if self.lo and val < self.lo:
            raise TypeError(
                f"Got {val!r}, which falls below range ({self.lo})"
            )
        if self.hi and val > self.hi:
            raise TypeError(
                f"Got {val!r}, which exceeds the range ({self.hi}) "
            )

        setattr(obj, self.name, val)


def typed(name: str) -> type:
    """
    Returns a new descriptor class with a single attribute named after self.

    The attribute is set by setting an instance of this descriptor on the target
    object. This can be done using the dot notation, or through calling it as a
    function (and passing the instance as first argument).

    >>> from pprint import pprint
    >>>
    >>> class Foo(object):
    ...     bar = typed('bar')
    ...
    >>>
    >>> pprint(Foo.bar)
    <some random object>

    If one wants to enforce specific values, they need to define the attributes
    `lo` and `hi`, e.g.

    >>> class Bar(object):
    ...     baz = typed('baz', lo=3, hi=7)
    ...
    >>>
    >>> pprint(Bar.baz)
    <some random object>
    """

    self = TypedDescriptor()
    self.name = ""
    return self


class TypedGenericMeta(type):
    def __new__(mcls, name, bases, namespace):

        attrs = {
            attr: TypedDescriptor() for attr in namespace.keys()
            if not attr.startswith("_")
        }
        return super().__new__(mcls, name, bases, namespace.update(attrs))

    # def __call__(cls, *args, **kwargs):
    #     instance = super().__call__(*args, **kwargs)
    #     for k, v in kwargs.items():
    #         setattr(instance, k, v)

    def __getitem__(cls, args):
        """Returns a subclass of cls that uses the given parameters."""

        if isinstance(args, tuple) and len(args) == 2:
            lo, hi = args
        else:
            raise ValueError("Arguments must be a pair.")

        return super().__new__(
            mcls,
            name,
            bases,
            {"__args__": args},
        )


@functools.total_ordering
class Point(metaclass=TypedGenericMeta):
    def __repr__(self):
        return f"<Point x={self.x}, y={self.y}>"

    def __eq__(self, other):
        try:
            return self.x == other.x and self.y == other.y
        except AttributeError as error:
            return False

    def __gt__(self, other):
        return abs(self.x**2 + self.y**2) > abs(other.x**2 + other.y**2)

    @classmethod
    def _validate_arguments(cls, x, y):
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError("x and y must be integers.")
        if x < 0 or y < 0:
            raise ValueError("x and y must be non-negative.")


# ── Classes ───────────────────────────────────────────────────────────────────

class Counter:
    count: dict[str, int] = {}

    def __init_subclass__(cls):
        cls.count = {}
        for attr in cls.__dict__.keys():
            cls.count[attr] = getattr(cls, attr).__get__()

    def inc(self, key, step=1):
        self.count[key] += step

    def dec(self, key, step=1):
        self.count[key] -= step


class Box:

    def __enter__(self):
        self._items = []
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is NotEnoughItemsException:
            raise exc_type
        
        elif exc_type is TooManyItemsException:
            raise exc_type
        
        else:
            pass


class BaseClass:

    def do_something(self, arg: str) -> str:
        return "Something happened"


class DerivedClass(BaseClass):

    def do_something(self, arg: str) -> str:
        return "Something totally different happened."


class PointWithXY(Point[int], Point[float]):
    ...


class PointWithXZ(Point[int]):

    def __init__(self, *, x: int, z: int):
        self.x = x
        self.z = z

    def get_xz_tuple(self) -> tuple[int]:
        return (self.x, self.z)


        day = 1
        hour = 0
        minute = 0
    
    # Convert the elapsed minutes back into hours and minutes
    elapsed_hours = elapsed_seconds // 3600
    elapsed_minutes = (elapsed_seconds % 3600) // 60

    # Print out the new date and time
    print(f"{year}/{month}/{day} {hour}:{minute}")

    # TODO: Add code here that measures the performance of Fibonacci calculations using a pool of processes.


    # Get the start time
    start_time = time.time()

    # Make a list of arguments for our Fibonacci function
    args_list = [(i,) for i in range(10)]

    # Use the ThreadPoolExecutor class to run multiple tasks concurrently
    executor = mp.Pool(processes=4)
    results = [executor.apply_async(func=fibonacci, args=args) for args in args_list]
    # Close the pool and wait for all tasks to complete
    executor.close()
    executor.join()

    # Get the end time
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time} seconds")

if __name__ == "__main__":
    main(sys.argv[1:])