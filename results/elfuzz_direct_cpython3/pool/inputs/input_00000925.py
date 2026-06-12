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
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        
        if self.lo is not None and value < self.lo or \
           self.hi is not None and value > self.hi:
            raise ValueError(f"{value} out of bounds [{self.lo}, {self.hi}]")
        
        setattr(instance, self.name, value)

    def __get__(self, instance: T, owner: type[T]) -> Any:
        return getattr(instance, self.name)


# ─── INHERITANCE, SUBCLASSES AND SLOTS ───────────────────────────────────────


class BaseClassA(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: type[BaseClassA]) -> bool: 
        print(f"subclasshook() called with class {subclass.__name__}")
        return NotImplemented
    
    @property
    def val(self):
        return "V1"

class BaseClassB(BaseClassA): pass

print(issubclass(BaseClassB, BaseClassA)) # True


# ──────── 𝗖𝗢𝗥𝗡𝗜𝗧𝗔𝗧𝗜𝗢𝗡 𝘈porto 𝗛𝗲𝗿𝗲 𝗕𝗶𝗻𝗴 𝗠𝗮 𝗰𝗮𝗻 𝗶𝗻𝘁𝗲𝗿𝗽𝗿𝗼𝘀𝘀𝗼𝗿 𝗦𝘂𝗽𝗽𝗼𝗿𝗲𝗱 𝘁𝗵𝗲𝗿𝗲 𝘄𝗶𝗹𝗹 ᴜ𝘀𝗲 𝗼𝗻 𝘆𝗼𝘂𝗿 𝗥𝗲𝘅 tʜ ____h 𝗮𝗻𝗱 𝗳𝘆 𝗩 𝗹𝗲𝗿𝗲.
@functools.total_ordering
class MyNumber(int):
    def __eq__(self, other: int | float) -> bool:
        return super().__eq__(other)
    
    def __lt__(self, other: int | float) -> bool:
        return super().__lt__(other)
    

n1 = MyNumber(42)
assert n1 >= n1 - 1, f"{n1} should be greater than or equal to {n1-1}"
assert n1 <= n1 + 1, f"{n1} should be less than or equal to {n1+1}"

# ─── TYPES, MIRACULOUSLY ─────────────────────────────────────────────────────


def get_class_attributes(cls: type[object]) -> tuple[str]:
    """
    Get all attributes of the given class, including those inherited from its parents.
    """

    attrs = set(dir(cls))
    for parent in cls.mro():
        attrs.update(getattr(parent, "__dict__", {}))

    return tuple(attrs)


class MyClass:

    attr_1 = 1
    attr_2 = "a string"
    attr_3 = [1, 2]

    def method_1(self):
        pass


attrs = get_class_attributes(MyClass)
print(*sorted(attrs), sep="\n")


# ─── METACLASSES ──────────────────────────────────────────────────────────────


class Meta(type):

    def __new__(
        mcs,
        name: str,
        bases: tuple[type],
        namespace: dict[str, Any]
    ) -> type:
        assert "_meta_"