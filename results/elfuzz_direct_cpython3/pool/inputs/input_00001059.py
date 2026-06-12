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
        value = getattr(obj, self.name)
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{value!r} must be an instance of {self.expected_type}")
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{value} less than minimum allowed ({self.lo})")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{value} greater than maximum allowed ({self.hi})")
        return value

    def __set__(self, obj, value):
        setattr(obj, self.name, value)


# ── Meta classes ──────────────────────────────────────────────────────────────

class TypedMeta(type):
    def __new__(cls, name: str, bases: tuple[type], namespace: dict[str, Any]):

        if "__slots__" in namespace:
            pass

        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, TypedDescriptor):
                attr_value.name = attr_name

        return super().__new__(cls, name, bases, namespace)


class MyClass(metaclass=TypedMeta):

    my_attr: str

# ── Context Managers ───────────────────────────────────────────────────────────

def context_manager(func: Callable[..., Optional[Awaitable[T]]]) -> Callable[..., T]:

    def wrapper(*args, **kwargs) -> T:
        with ContextManager() as cm:
            result = func(*args, **kwargs)
            if result is not None:
                yield result
        return result

    return wrapper


@contextlib.contextmanager
def ContextManager():

    try:
        yield
    finally:
        print("Context manager finished.")


# ── Generators ────────────────────────────────────────────────────────────────

@functools.wraps(generate_range)
def generate_range_from_to(lo: int, hi: int) -> Generator[int]:
    while lo <= hi:
        yield (lo := lo + 1)


@generate_range_from_to(5, 9)
def generate_even_numbers() -> Iterator[int]: ...


# ── Decorators ────────────────────────────────────────────────────────────────

def count_calls(fun: FunctionType) -> FunctionType:
    
    @functools.wraps(fun)
    def wrapped_fun(*args, **kwargs):
        wrapped_fun.count += 1
        return fun(*args, **kwargs)

    wrapped_fun.count = 0
    return wrapped_fun


@count_calls
async def async_function(a: int, b: int) -> int:
    return a * b


# ── Classes ───────────────────────────────────────────────────────────────────

class _Singleton(ABC):
    __singleton_: ClassVar[Optional[_Singleton]] = None

    def __call__(self):
        if self.__singleton_ is None:
            self.__singleton_ = self.__create_instance__()
        
        return self.__singleton_

    @abstractmethod
    def __create_instance__(self) -> _Singleton:
        ... # noqa: E704


class Singleton(_Singleton):

    def __create_instance__(self) -> Singleton:
        return Singleton()


if __name__ == "__main__":
    ...