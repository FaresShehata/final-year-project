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

    # This class defines two abstract methods.
    @classmethod
    @abc.abstractmethod
    def validate(cls, value: Any) -> None:
        ...

    def __get__(self, instance: object, owner: object | None) -> any:
        return self._value
    
    def __set__(self, instance: object, value: Any) -> None:
        self.validate(value)
        self._value = value

    def __delete__(self, instance: object) -> None:
        del self._value


class IntTyped(TypedDescriptor):
    @classmethod
    def validate(cls, value: int) -> None:
        assert isinstance(value, int), "Not an integer!"


class FloatRangeTyped(TypedDescriptor):

    MIN_VALUE: ClassVar[float]
    MAX_VALUE: ClassVar[float]

    @classmethod
    def validate(cls, value: float) -> None:
        assert (
            cls.MIN_VALUE <= value <= cls.MAX_VALUE
        ), f"Not within range {cls.MIN_VALUE}-{cls.MAX_VALUE}"


class DTypeMeta(type):
    def __new__(
        cls: type[Dtype],
        name: str,
        bases: tuple[type[Any], ...],
        namespace: dict[str, object],
    ) -> dtype[Any]:
        if "__slots__" not in namespace or not namespace.get("__slots__", []):
            raise RuntimeError(f"Class {name} must have slots.")
        
        if "__init__" not in namespace:
            raise RuntimeError(
                f"Classes with slots must define an __init__ constructor."
            )
        
        return super().__new__(cls, name, bases, namespace)

    def __call__(cls: dtype[T], *args: args[T], **kwargs: kwargs[T]) -> T:
        inst = super().__call__(*args, **kwargs)
        cls.check_slots(inst)
        return inst
    
    @staticmethod
    def check_slots(obj: Any) -> None:
        """
        Check that the provided object has all of its defined slots set.
        """

        for slot in obj.__dict__.keys():
            if not hasattr(slot, "__slot__"):
                continue
            
            slot_name = slot.__slot__
            
            if slot_name not in obj.__slots__:
                raise AttributeError(
                    f"{obj.__class__.__name__}.{slot_name} is missing from "
                    f"{obj}."
                )


class Dtype(metaclass=DTypeMeta):
    pass



# ─── CLASSES ─    
    def __repr__(self) -> str:
        repr_str = f"{self.__class__.__name__}"
        for attr in dir(self):
            if not attr.startswith("__"):
                val = getattr(self, attr)
                repr_str += f"\n\t{name}={val}"
        return repr_str


class ConcreteClassA(BaseClassA):
    _a_attr: int = 42
    b_attr: float = 3.14
    c_attr: complex = 1j + 1j
    d_attr: str = "foo"


# ─── METACLASS ───────────────────────────────────────────────────────────────


def meta_factory(name, bases, attrs) -> type[Any]:
    """A factory function for creating new metaclasses."""
    attrs["hello"] = "world!"
    return type(name, bases, attrs)


# ─── STATIC AND CLASS METHODS ────────────────────────────────────────────────

class StaticExample:
    cls_var: staticmethod[int] = staticmethod(lambda x: x ** 2)
    obj_var: methodcaller("func") = lambda self, x: x * 5


@functools.cache
def memoized_func(x: int) -> int:
    return x**2


@contextlib.contextmanager
def open_file(filename: str, mode="r") -> Iterator[None]:
    try:
        file = open(filename, mode)
        yield
    finally:
        file.close()



# ─── GENERATORS ──────────────────────────────────────────────────────────────