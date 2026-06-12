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
    
    @classmethod
    def __prepare__(metacls, clsname, bases): # pylint: disable=unused-argument
        return super().__prepare__(clsname, bases)
    
    def __new__(metacls, clsname, bases, clsdict):
        cls = super().__new__(metacls, clsname, bases, clsdict)
        cls._registry.append(cls)
        return cls
    
    @property
    def registry(cls) -> list[type]:
        return cls._registry or []
    
    _registry: ClassVar[list[type]] = []


# ─── Custom Types ─────────────────────────────────────────────────────────────

class SortedList(list):

    def sort(self,
             key=lambda x: x,
             reverse=False,
             /,
             *,
             keyfunc=str.casefold,
             ascending=True,
             case_sensitive=False,
             ):
        # TODO: refactor to support multiple keys
        if not hasattr(keyfunc, "__call__"):
            raise TypeError("'keyfunc' must be callable.")
        
        if case_sensitive:
            self.sort(key=keyfunc, reverse=reverse)
        else:
            # TODO: refactor using 'functools.cmp_to_key' instead of defining custom key function.
            sorted_list = sorted([item for item in self], 
                                 key=(lambda item: (keyfunc(item), item)),
                                 reverse=reverse)
            super().extend(sorted_list)



# ─── Abstract Base Classes ────────────────────────────────────────────────────

class Animal(metaclass=RegistryMeta):
    pass


class Carnivore(Animal):
    pass


class Herbivore(Animal):
    pass


class Omnivore(Carnivore, Herbivore):
    pass


class Cheetah(Omnivore):
    pass


class Lion(Omnivore):
    pass


def get_all_subclasses(class_: type) -> list[type]:
    """Return all direct and indirect subclasses of the given class."""
    subclasses = []
    queue = [class_]
    
    while queue:
        current_class = queue.pop()
        
        for subclass in current_class.__subclasses__():
            if subclass not in subclasses:
                queue.insert(0, subclass)  # insert at beginning so we can detect circular inheritance
                subclasses.append(subclass)
    
    return subclasses  # pylint: disable=redundant-return-value


CARNIVORES = get_all_subclasses(Carnivore)
HERBIVORAE = get_all_subclasses(Herbivore)
OMNIVORATES = get_all_subclasses(Omnivore)
ANIMALS = get_all_subclasses(Animal)  # pylint: disable=invalid-name

assert len(ANIMALS) == 2 + sum(len(x) for x in CARNIVORES, len(HERBIVORAE)), "Classes are missing"
assert set(getattr(a, "name") for a in ANIMALS) == {"Cheetah", "Lion"}, "Class names mismatch"

assert set(getattr(c, "name") for c in CARNIVORES) == {"Omnivore", "Carnivore"}
assert set(getattr(h, "name") for h in HERBIVORAE) == {"Herbivore", "Herbivore"}
assert set(getattr(o, "name") for o in OMNIVORATES) == {"Carnivore", "Herbivore"}

for c in CARNIVORES:
    assert issubclass(c, Carnivore)
    assert issubclass(c, Animal)
    assert issubclass(c, Herbivore)
    assert issubclass(c, Omnivore)

for h in HERBIVORAE:
    assert issubclass(h, Herbivore)
    assert issubclass(h, Animal)
    assert issubclass(h, Carnivore)
    assert issubclass(h, Omnivore)

for o in OMNIVORATES:
    assert issubclass(o, Omnivore)
    assert issubclass(o, Animal)
    assert issubclass(o, Carnivore)
    assert issubclass(o, Herbivore)

for