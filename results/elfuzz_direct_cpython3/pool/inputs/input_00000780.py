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



# ─── CLASSES ─     ────────────────────────────────────────────────────────────

@DType.register
class Number(DTYPE):
    __slots__ = ("_value",)

    _MIN_VALUE: ClassVar[int] = -sys.maxsize - 1
    _MAX_VALUE: ClassVar[int] = sys.maxsize

    def __init__(self, value: int) -> None:
        self.value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self.validate(value)
        self._value = value
        
    def validate(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Value must be an integer")
        
        if (not self._MIN_VALUE < value < self._MAX_VALUE):
            raise ValueError(
                f"Value must be between {self._MIN_VALUE} and {self._MAX_VALUE}"
            )



@DType.register
class PositiveNumber(Number):
    _MIN_VALUE: ClassVar[int] = 0


# ─── TYPES ────────────────────────────────────────────────────────────────────

def dataclasses_to_types(cls: Type[object]) -> Type[object]:
    """Convert dataclasses to typed classes."""
    
    for base in cls.mro():
        if issubclass(base, Dataclass):
            break
        
    else:
        raise NotImplementedError("This method only works on dataclasses.")
    
    new_bases = tuple([base for base in base.mro() if base != Dataclass])
    new_meta = type(cls).__bases__[0]
    new_cls = type(cls)(cls.name, new_bases, {"__dataclass_fields__": cls.fields})
    
    return new_cls



@functools.total_ordering
class Dataclass(object):
    """Dataclass that enforces named fields as typed objects."""
    
    __slots__: list[str] = ["fields"]
    
    name: ClassVar[str]
    fields: ClassVar[dict[str, Field]]
    
    def __post_init__(self) -> None:
        for field in self.field_values.values():
            field.raise_if_not_set()
            
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        
        return hash(tuple(sorted(self.items()))) == hash(tuple(sorted(other.items())))
