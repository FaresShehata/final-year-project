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
        elif self.lo is not None and value < self.lo or self.hi is not None and value > self.hi:
            raise ValueError(
                f"{self.name}: value must be between {self.lo} and {self.hi}"
            )
        setattr(obj, self.name, value)


class IntegerDescriptor(TypedDescriptor):
    """Integer descriptor with integer-only support."""
    
    def __init__(self, lo=None, hi=None):
        super().__init__(int, lo=lo, hi=hi)
        
    @classmethod
    # noinspection SpellCheckingInspection
    def from_range(cls, lo: int, hi: int) -> IntegerDescriptor:
        return cls(lo=lo, hi=hi)


class FloatDescriptor(TypedDescriptor):
    """Float descriptor with float-only support."""
    
    def __init__(self, lo=None, hi=None):
        super().__init__(float, lo=lo, hi=hi)
        
    @classmethod
    # noinspection SpellCheckingInspection
    def from_range(cls, lo: float, hi: float) -> FloatDescriptor:
        return cls(lo=lo, hi=hi)


class StringDescriptor(TypedDescriptor):
    """String descriptor with string-only support."""

    def __init__(self, pattern: str | None = None):
        super().__init__(str)
        self.pattern = pattern
        
    @property
    def pattern(self) -> str:
        return self._pattern
    
    @pattern.setter
    def pattern(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f'{self.__class__.__name__}: "{value}" is not a string')
        self._pattern = value


#
# ─── CLASSES ───────────────────────────────────────────────────────────────────
#

class BaseClass:

    _default_attrs: ClassVar[dict[str, Any]] = dict()
    _defaults: ClassVar[dict[str, Any]]

    def __init_subclass__(cls, **kwargs) -> None:
        """Initialize class-level defaults by merging in the default attributes of its base classes.
        
        NOTE:
            The `metaclass` attribute will be added to all subclasses.
            This can be used to set a custom metaclass for the subclass.
        """
        super().__init_subclass__(**kwargs)
        for key, attr in cls._default_attrs.items():
            try:
                setattr(cls, key, attr)
            except AttributeError as