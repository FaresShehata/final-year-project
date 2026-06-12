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
                f"{obj} must be {self.expected_type} but got {value}."
            )
        if self.lo is not None and value < self.lo or self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name} must lie between {self.lo} and {self.hi}")
        setattr(obj, self.name, value)

    def __delete__(self, obj):
        delattr(obj, self.name)

class ReadableTypedDescriptor(TypedDescriptor):

    def __get__(self, obj, objtype=None):
        try:
            return super().__get__(obj, objtype=objtype)
        except AttributeError as e:
            if hasattr(obj, "is_readonly") and obj.is_readonly:
                raise PermissionError(f"{e.args[0]} - Cannot set read-only")
            raise

class IntegerReadDescriptor(ReadableTypedDescriptor[int]):
    def __init__(self, lo: int | None = None, hi: int | None = None):
        super().__init__(int=lo, hi=hi)

    def __set__(self, obj, value):
        if isinstance(value, float):
            value = round(value)
        if not isinstance(value, int):
            raise TypeError(f"{value} must be an integer.")
        return super().__set__(obj, value)

class PositiveIntegerReadDescriptor(IntegerReadDescriptor):
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError("Must be positive.")
        return super().__set__(obj, value)



# ─── Example Usage ────────────────────────────────────────────────────────────

class Point:

    x: int = IntegerReadDescriptor(-2 ** 30, 2**30-1)
    y: int = IntegerReadDescriptor(lo=-2 ** 30, hi=2**30-1)

    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
print(p.x, p.y)
try:
    # This should error out since we can't have negative coordinates.
    p.x = -1
except:
    ...

try:
    p.z = 6
except:
    ...
try:
    # This should error out since z isn't initialized by default.
    p.z = 7
except:
    ...

try:
    p.x = 1.9
except:
    ...

                return other

    @classmethod
    def get_min_max(cls):
        """
        Returns the minimum and maximum values of a given enum type.
        :return: tuple[min_value, max_value]
        """
        return (min(x.value for x in cls), max(x.value for x in cls))

    def __lt__(self, other: "Byte"):
        if isinstance(other, int):
            return self.value < other
        else:
            return self.value < other.value


def get_byte():
    return Byte.from_str(random.choice(list(Byte.__members__)))


# ---------------------------------------------------------


@dataclasses.dataclass(slots=True)
class Node:
    val: float

    def __post_init__(self):
        pass

    def __hash__(self):
        return hash((type(self), self.val))
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.val == other.val
        elif isinstance(other, numbers.Number):
            return self.val == other

    __setattr__ = property(lambda self, key, value: None, lambda self, value: None)
    __delattr__ = property(lambda self, attr: None, lambda self, value: None)

    def __repr__(self):
        return f"<Node({self.val})>"

    def __str__(self):
        return "<Node>" + repr(self)

    def __format__(self, format_spec):
        return f'<Node<{format_spec}>'

@dataclasses.dataclass(slots=True)
class BinaryNode(Node):
    left_child: "BinaryNode" = dataclasses.field(default_factory=lambda: NullNode())
    right_child: "BinaryNode" = dataclasses.field(default_factory=lambda: NullNode())

    def __post_init__(self):
        if self.left_child is not None:
            self.left_child.parent = self
        if self.right_child is not None:
            self.right_child.parent = self
    
    def __iter__(self):
        if self.left_child is not None:
            yield from self.left_child
        yield self
        if self.right_child is not None:
            yield from self.right_child

@dataclasses.dataclass(slots=True)
class NullNode(BinaryNode):
    pass

# ---------------------------------------------------------



if __name__ == '__main__':
    try:
        p.x = 1
    except Exception as e:
        print(e)

    try:
        p.x = 1.5
    except Exception as e:
        print(e)

    try:
        p.x = -1
    except Exception as e:
        print(e)

    print(p.x, p.y)