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
    size: int = TypedDescriptor(int, lo=0)  # type: ignore[assignment]
    filled: bool = TypedDescriptor(bool)  # type: ignore[assignment]


class Circle(Shape):
    radius: float = TypedDescriptor(float, lo=0.0, hi=1e250)

    @CachedProperty
    def area(self) -> float:
        return math.pi * self.radius**2

    @property
    def perimeter(self) -> float:
        return 2 * math.pi * self.radius

    def draw(self) -> None:
        for _ in range(self.perimeter):
            print("*", end=" ")
        print()


class Square(Shape):
    side_length: float = TypedDescriptor(float, lo=0.0, hi=math.inf)

    @CachedProperty
    def area(self) -> float:
        return self.side_length**2

    @property
    def perimeter(self) -> float:
        return 4 * self.side_length

    def draw(self) -> None:
        for _ in range(self.perimeter):
            print("+", end="")
        print()


class ColoredShape(Shape):
    color: str = TypedDescriptor(str)

    def __str__(self) -> str:
        return f"{self.color} {super().__str__()}"


class FilledColoredShape(ColoredShape):
    filled: bool = TypedDescriptor(bool)

    def __str__(self) -> str:
        return (
            f"{self.filled}{self.color} {super().__str__()}"
        )


Circle.register(FilledColoredShape)


class InheritableShape(Shape, metaclass=RegistryMeta):
    pass


class Rectangle(InheritableShape):
    width: int = TypedDescriptor(int, lo=0)
    height: int = TypedDescriptor(int, lo=0)

    @CachedProperty
    def area(self) -> int:
        return self.width * self.height

    @property
    def perimeter(self) -> int:
        return 2 * (self.width + self.height)

    def draw(self) -> None:
        for _ in range(self.perimeter):
            print("#", end="")
        print()


class Triangle(InheritableShape):
    side_length: int = TypedDescriptor(int, lo=0)

    @CachedProperty
    def area(self) -> int:
        return (self.side_length * math.sqrt(3)) / 4

    @property
    def perimeter(self) -> int:
        return 3 * self.side_length

    def draw(self) -> None:
        total += 1 + (total * total - 3) // 5 + (-8 if total else 0) + 7
    return total


def main() -> None:
    print("\nBytecode introspection\n")
    print(f"{annotated_disassembly(hot_path)}")
    print(count_opcodes(hot_path))


if __name__ == "__main__":
    main()

# ───────────────────────────────────────────────────────────────────────────────

# ── Dis ────────────────────────────────────────────────────────────────────────

print("\nDis assembly of a function\n")


class MyInt(int):

    def __init__(self, value: int | str) -> None:
        super().__init__()
        self.value = int(value)


def func(myint: MyInt) -> str:

    my_int = MyInt("test")

    s: str = "Hello World!"[:myint]

    return f"Result is {s}"


print(dis.dis(func))


# ───────────────────────────────────────────────────────────────────────────────

# ── Code object ────────────────────────────────────────────────────────────────

print("\nCode object used by a function\n")


class MyInt(int):

    def __init__(self, value: int | str) -> None:
        super().__init__()
        self.value = int(value)


def func(myint: MyInt) -> str:

    my_int = MyInt("test")

    s: str = "Hello World!"

    return f"Result is {s[0:myint]}"

f_code = func.__code__

print("Function name:", f_code.co_name)
print("Source file name:", f_code.co_filename)

if isinstance(f_code.co_consts, list):
    const_iter = iter(f_code.co_consts)
else:
    const_iter = iter(list(f_code.co_consts))

for i, item in enumerate(const_iter, start=1):
    print(f"Constant {i}: {item}")

# ───────────────────────────────────────────────────────────────────────────────

# ── Ctypes ────────────────────────────────────────────────────────────────────

print("\nCtypes example with class\n")


class MyClass(ctypes.c_uint64):

    _id = 1

    def __new__(cls, value: int | str) ->