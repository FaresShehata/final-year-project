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
class Descr:
    def __init__(self) -> None:
        self.value: int | str = 0

    @property
    def value(self) -> int | str:
        return self.__value
    
    # @value.setter
    # def value(self, new_value: int|str):
    #     print(f"Setting {type(new_value)}")
    #     self.__value = new_value

    @value.getter
    def value(self):
        
        if isinstance(self.__value, str):
            return f"{len(self.__value)}"
        
        return self.__value


descr_01 = Descr()
print(descr_01.value)
descr_01.value = "Hello"
print(descr_01.value)

del descr_01.value
#print(descr_01.value)


# ── Metaclasses ──────────────────────────────────────────────────────────────
class Meta(type):
    """Metaclass example"""

    pass

# class MyClass(metaclass=Meta):
#     ...


# ── Context Managers ──────────────────────────────────────────────────────────
@contextlib.contextmanager
def func() -> Generator[int]:
    yield 42


with func():
    print("Inside the with statement")


# ── Generators ───────────────────────────────────────────────────────────────
def gen() -> Generator[str]:
    for i in range(3):
        yield str(i + 1)


for i in gen():
    print(i)


# ── Decorators ───────────────────────────────────────────────────────────────
def decorator(func: types.FunctionType) -> Callable[[Any], Any]:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        result = func(*args, **kwargs)
        
        print(result)
        return result

    return wrapper


@decorator
def add(a: int, b: int) -> int:
    return a + b

add(5, 6)



# ── Abstract Base Classes ────────────────────────────────────────────────────
class Shape(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, C: Type[Any]) -> bool:
        """Check if an object is a subclass of 'Shape' and returns True."""
        if cls is Shape:
            attrs = {
                "__call__",
                "__iter__",
                "__len__",
                "__contains__",
                "__getitem__",
                "__setitem__",
                "__delitem__",
                "__eq__",
                "__ne__",
                "__lt__",
                "__le__",
                "__gt__",
                "__ge__",
                "__and__",
                "__or__",
                "__xor__",
                "__rand