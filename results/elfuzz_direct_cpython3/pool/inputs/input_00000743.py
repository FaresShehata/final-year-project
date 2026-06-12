"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroups.

This is a small demonstration of how to write tests that are independent from the environment.
"""

import asyncio

from dataclasses import dataclass
from functools import wraps
from math import sqrt
from random import randint as _randint

from pytestqt.qt_compat import qt_api


@dataclass(frozen=True)
class Point:
    x: float
    y: float


def test_structural_pattern_matching():
    """Structural Pattern Matching."""

    def is_point(obj) -> bool:
        return hasattr(obj, "x") and hasattr(obj, "y")

    assert is_point(Point(1.0, 2.0))
    assert not is_point("foo")
    assert not is_point(None)


async def test_async_await(qtbot):
    """Async Await."""
    await qtbot.wait(500)

    class Foo:

        @property
        def bar(self):
            return self._bar

        @bar.setter
        def bar(self, value):
            self._bar = value

    foo = Foo()
    foo.bar = "baz"


def test_protocols():
    """
    Protocol.

    A protocol defines a set of methods or attributes that must be implemented by any class that implements it.
    """

    class Shape:
        def area(self) -> float:
            ...

    class Circle(Shape):
        def area(self) -> float:
            return 3.14 * (self.radius ** 2)

        radius: float

    circle = Circle()
    circle.radius = 2.0
    assert circle.area() == 12.56998729570998


def test_data_classes():
    """Data classes."""

    @dataclass(frozen=True)
    class Point:
        x: int
        y: int

    point = Point(x=1, y=2)
    assert str(point) == "(1, 2)"
    # point.x = 5
    assert point.x == 1
    frozen = True


def test_slots():
    """Slots."""

    class Point:
        __slots__ = ("x", "y")

        def __init__(self, x: int, y: int) -> None:
            super().__setattr__("x", x)
            super().__setattr__("y", y)

    point = Point(1, 2)
    assert str(point) == "(1, 2)"
    # point.x = 5
    assert point.x ==            pass
        else:
            setattr(rand, "__wrapped__", rand)
            setattr(rand, "__qualname__", f"{rand.__qualname__}({module}.randint)")
            setattr(rand, "__annotations__", {})
            setattr(rand, "__defaults__", ())
            setattr(rand, "__code__", rand.__code__)
            setattr(rand, "__dict__", rand.__dict__)
            setattr(rand, "__kwdefaults__", rand.__kwdefaults__)
            setattr(rand, "__self__", rand.__self__)
            setattr(rand, "__weakref__", rand.__weakref__)
            for attribute in dir(module):
                value = getattr(rand, attribute)
                if callable(value):
                    setattr(rand, attribute, value)
    seed = seed % (2 ** 31)
    if seed < 0:
        seed += 2 ** 31
    for module in (
        "decimal",
        "fractions",
        "ipaddress",
        "numbers",
        "random",
        "re",
