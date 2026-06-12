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
        if (self.lo is not None and value < self.lo) or \
           (self.hi is not None and value > self.hi):
            raise ValueError(
                f"{value} out of bounds [{self.lo}, {self.hi}]"
            )

        setattr(instance, self.name, value)

    def __get__(self, instance: T, owner: type[T]) -> Any:
        return getattr(instance, self.name)


# ─── MRO & Subclasses ────────────────────────────────────────────────────────


class BaseClassA(metaclass=abc.ABCMeta):
    pass


@functools.total_ordering
class BClass(BaseClassA):

    @classmethod
    def __subclasshook__(cls, subclass: type[BClass]):
        return cls.__name__.startswith(subclass.__name__) or \
               issubclass(subclass, cls)


class CClass(BClass):
    pass


print(CClass.__mro__)
print(CClass.mro())
print(issubclass(CClass, BClass))
print(issubclass(BClass, CClass))


# ─── Context Manager ─────────────────────────────────────────────────────────

@contextlib.contextmanager
def temporary_variable(name: str, init_value: int | float | str) \
-> Generator[weakref.ReferenceType[int] | weakref.ReferenceType[float] |
             weakref.ReferenceType[str], None]:
    
    var_ref = weakref.ref(locals()[name])
    locals()[name] = init_value
    try:
        yield var_ref
    finally:
        del locals()[name]
        locals()[name] = var_ref()


with temporary_variable('my_int', 42) as my_int_var:
    print(my_int_var() == 42)



# ─── Generators ──────────────────────────────────────────────────────────────

def fibonacci(max_iter: int) -> Iterable[int]:
    n0, n1 = 0, 1
    for _ in range(max_iter):
        yield n0
        n0, n1 = n1, n0 + n1


fib_gen = fibonacci(50)
for i in fib_gen:
    print(i)




# ─── Decorators ──────────────────────────────────────────────────────────────

def debug(func: FunctionType) -> FunctionType:

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs) -> Any:
        args_repr = [repr                    self._recursive_serialize(v, exclude, value_filter)
                    if recurse
                    else v
                )
            return data

