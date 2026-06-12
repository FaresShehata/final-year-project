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


d = Descr()
print(d.value)
# d.value = 42

# ─── Context manager ─────────────────────────────────────────────────────────
@contextlib.contextmanager
def my_context():
    """Context manager that prints a message before and after the code block."""
    
    print('Entering...')
    yield
    print('Exiting...')

with my_context():
    print('Inside the with block.')

# ─── Generators ─────────────────────────────────────────────────────────────
def my_gen() -> Generator[int, int, None]:
    '''Generates numbers from 0 to n-1.'''
    for num in range(5):
        yield num
        
gen = my_gen()

for i in gen:
    print(i)

next(gen)
next(gen)
try:
    next(gen)
except StopIteration as e:
    print(e)


# ───────────────────────────────────────────────────────────────────────────
class MyClass(metaclass=abc.ABCMeta):
    '''
    Base class for all classes.
    '''

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        """
        Returns True if the given class is a subclass of MyClass,
        False otherwise.

        For example, this function will be called when checking whether
        a class is a subclass of MyClass. The following code will return
        True:

            >>> class MySubClass(MyClass): ... 
            >>> MyClass.subclasshook_(MySubClass)
            True

        However, the following code will return False:

            >>> class AnotherSubClass(object): ...
            >>> MyClass.subclass_hook_(AnotherSubClass)
            False

        """
        return (
            hasattr(subclass, "method") and callable(getattr(subclass, "method"))
            or NotImplemented
        )
        
    def method(self) -> None:
        """A method of MyClass."""


class SubClass(MyClass):
    """
    A subclass of MyClass.
    """

    def method(self) -> None:
        """A method of SubClass."""

sub = SubClass()
assert isinstance(sub, MyClass)

# ─── Decorator ──────────────────────────────────────────────────────────────
class MyDecorator:
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print("Before calling %s." % func.__name__)
            result = func(*args, **kwargs)
            print("After calling %s." % func.__name__)
            return result
        return wrapper

# ════════════════════════════════════════════════════════════════════════════
@MyDecorator()
def my_function(x, y):
    return x * y

my_function(3, 4)


# ───────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    pass