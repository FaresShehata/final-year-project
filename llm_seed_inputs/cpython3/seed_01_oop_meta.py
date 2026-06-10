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
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""

    _registry: dict[str, type] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if not inspect_abstract(cls):
            RegistryMeta._registry[name] = cls
        return cls

    def __repr__(cls) -> str:
        return f"<class '{cls.__qualname__}' via RegistryMeta>"


def inspect_abstract(cls) -> bool:
    return bool(getattr(cls, "__abstractmethods__", False))


# ── Abstract base ─────────────────────────────────────────────────────────────

class Shape(metaclass=RegistryMeta):
    color: str = TypedDescriptor(str)  # type: ignore[assignment]

    def __init__(self, color: str = "white"):
        self.color = color

    @abc.abstractmethod
    def area(self) -> float: ...

    @abc.abstractmethod
    def perimeter(self) -> float: ...

    @CachedProperty
    def label(self) -> str:
        return f"{type(self).__name__}(color={self.color})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(area={self.area():.4f})"

    def __lt__(self, other: Shape) -> bool:
        return self.area() < other.area()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shape):
            return NotImplemented
        return type(self) is type(other) and self.area() == other.area()

    def __hash__(self) -> int:
        return hash((type(self).__name__, round(self.area(), 8)))


import math

class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, radius: float, color: str = "red"):
        super().__init__(color)
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    width: float  = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]
    height: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, width: float, height: float, color: str = "blue"):
        super().__init__(color)
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Triangle(Shape):
    a: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]
    b: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]
    c: float = TypedDescriptor(float, lo=0.0)  # type: ignore[assignment]

    def __init__(self, a: float, b: float, c: float, color: str = "green"):
        super().__init__(color)
        self.a, self.b, self.c = a, b, c

    def area(self) -> float:
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

    def perimeter(self) -> float:
        return self.a + self.b + self.c


# ── Decorators ────────────────────────────────────────────────────────────────

def retry(times: int = 3, exceptions: tuple = (Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc: Optional[Exception] = None
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
            raise RuntimeError(f"Failed after {times} attempts") from last_exc
        return wrapper
    return decorator


def trace(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        print(f"  CALL {fn.__name__}({args!r}, {kwargs!r})")
        result = fn(*args, **kwargs)
        print(f"  RETURN {fn.__name__} -> {result!r}")
        return result
    return wrapper


class memoize:
    """Class-based decorator for memoization."""
    def __init__(self, fn):
        self.fn = fn
        self.cache: dict = {}
        functools.update_wrapper(self, fn)

    def __call__(self, *args):
        if args not in self.cache:
            self.cache[args] = self.fn(*args)
        return self.cache[args]

    def cache_info(self) -> dict:
        return {"size": len(self.cache), "keys": list(self.cache.keys())}


@memoize
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# ── Context managers ──────────────────────────────────────────────────────────

class ManagedArena:
    """Context manager that tracks resource acquisition."""

    _instances: ClassVar[list[weakref.ref]] = []

    def __init__(self, name: str):
        self.name = name
        self.shapes: list[Shape] = []
        self._active = False
        ManagedArena._instances.append(weakref.ref(self))

    def __enter__(self) -> ManagedArena:
        self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self._active = False
        if exc_type is ValueError:
            print(f"  Arena {self.name!r}: suppressed ValueError({exc_val})")
            return True  # suppress
        return False

    def add(self, shape: Shape) -> None:
        if not self._active:
            raise RuntimeError("Arena not active")
        self.shapes.append(shape)

    def total_area(self) -> float:
        return sum(s.area() for s in self.shapes)

    def __repr__(self) -> str:
        return f"ManagedArena({self.name!r}, shapes={len(self.shapes)})"


@contextlib.contextmanager
def loud_section(title: str) -> Generator[None, None, None]:
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")
    try:
        yield
    finally:
        print(f"  [done: {title}]")


# ── Generators & itertools ────────────────────────────────────────────────────

def shape_stream(n: int) -> Iterator[Shape]:
    """Infinite-ish generator of cycling shapes."""
    factories = itertools.cycle([
        lambda i: Circle(float(i % 10 + 1)),
        lambda i: Rectangle(float(i % 7 + 1), float(i % 5 + 1)),
        lambda i: Triangle(3.0 + i % 3, 4.0, 5.0),
    ])
    for i, factory in zip(range(n), factories):
        yield factory(i)


def running_stats(shapes: Iterator[Shape]):
    """Generator pipeline: yield (count, cumulative_area, max_area) tuples."""
    cum = 0.0
    best = 0.0
    for k, s in enumerate(shapes, 1):
        a = s.area()
        cum += a
        best = max(best, a)
        yield k, cum, best


# ── __slots__ & __init_subclass__ ────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "z", "mass")

    def __init__(self, x: float, y: float, z: float, mass: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.mass = mass

    def distance_to(self, other: Particle) -> float:
        return math.sqrt(
            (self.x - other.x) ** 2 +
            (self.y - other.y) ** 2 +
            (self.z - other.z) ** 2
        )

    def __repr__(self) -> str:
        return f"Particle({self.x}, {self.y}, {self.z})"


class Plugin:
    _plugins: ClassVar[dict[str, type]] = {}

    def __init_subclass__(cls, tag: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if tag:
            Plugin._plugins[tag] = cls

    def run(self) -> str:
        return f"{type(self).__name__}.run()"


class AlphaPlugin(Plugin, tag="alpha"):
    def run(self) -> str:
        return "alpha output"

class BetaPlugin(Plugin, tag="beta"):
    def run(self) -> str:
        return "beta output"


# ── Dynamic class creation & exec ─────────────────────────────────────────────

def make_vector_class(dim: int) -> type:
    """Dynamically construct an N-dimensional vector class."""
    fields = [f"x{i}" for i in range(dim)]
    ns: dict[str, Any] = {}
    exec(
        "def __init__(self, " + ", ".join(f"{f}=0.0" for f in fields) + "):\n"
        + "\n".join(f"    self.{f} = {f}" for f in fields),
        ns,
    )
    exec(
        "def magnitude(self):\n"
        "    return __import__('math').sqrt("
        + "+".join(f"self.{f}**2" for f in fields)
        + ")",
        ns,
    )
    exec(
        "def __repr__(self):\n"
        "    vals = [" + ",".join(f"self.{f}" for f in fields) + "]\n"
        "    return f'Vec" + str(dim) + "({vals})'",
        ns,
    )
    return types.new_class(
        f"Vec{dim}",
        (),
        {},
        lambda d: d.update(ns),
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    with loud_section("Registry"):
        print("  Registered shapes:", list(RegistryMeta._registry.keys()))

    with loud_section("Descriptor validation"):
        c = Circle(5.0, color="cyan")
        print(f"  {c!r}, label={c.label!r}")
        try:
            c.radius = -1.0
        except ValueError as exc:
            print(f"  Caught expected: {exc}")

    with loud_section("ManagedArena"):
        with ManagedArena("primary") as arena:
            for shape in shape_stream(12):
                arena.add(shape)
            print(f"  {arena}")
            print(f"  total_area = {arena.total_area():.4f}")
            # Exercise suppression
            raise ValueError("test suppression")

    with loud_section("Generator pipeline"):
        stats = list(running_stats(shape_stream(8)))
        for count, cum, best in stats:
            print(f"  n={count:2d}  cum={cum:.3f}  best={best:.3f}")

    with loud_section("Fibonacci memoize"):
        vals = [fibonacci(n) for n in range(20)]
        print(f"  fib(0..19) = {vals}")
        print(f"  cache info = {fibonacci.cache_info()}")

    with loud_section("Particle __slots__"):
        ps = [Particle(i * 1.1, i * 0.9, i * 0.5) for i in range(5)]
        dists = [ps[i].distance_to(ps[i + 1]) for i in range(len(ps) - 1)]
        print(f"  consecutive distances: {[round(d, 4) for d in dists]}")

    with loud_section("Plugin __init_subclass__"):
        for tag, cls in Plugin._plugins.items():
            print(f"  [{tag}] => {cls().run()}")

    with loud_section("Dynamic class (exec)"):
        Vec3 = make_vector_class(3)
        v = Vec3(1.0, 2.0, 3.0)
        print(f"  {v!r}  magnitude={v.magnitude():.4f}")

    with loud_section("Sorted shapes with __lt__"):
        shapes = list(shape_stream(9))
        shapes.sort()
        for s in shapes:
            print(f"  {s!r}")

    with loud_section("functools.reduce + operator"):
        areas = [s.area() for s in shape_stream(6)]
        product = functools.reduce(operator.mul, areas, 1.0)
        print(f"  product of first-6 areas = {product:.4f}")


if __name__ == "__main__":
    main()
