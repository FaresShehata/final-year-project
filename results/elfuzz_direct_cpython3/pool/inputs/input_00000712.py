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


class CachedProperty(TypedDescriptor):
    """A property whose value is computed once per instance and then replaced."""
    
    def __init__(self, func):
        self.func = func
        self.name: str = ""
        
    def __set_name__(self, owner, name):
        self.name = name
        
    def __get__(self, obj, cls):
        if obj is None:
            return self
        val = obj.__dict__[self.name] = self.func(obj)
        return val


# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(type):

    def __prepare__(metacls, name, bases, **kwargs):  # type: ignore[misc]
        return {}

    def __new__(
            metacls,
            name: str,
            bases: tuple[type],
            namespace: dict[str, Any],
            **kwargs: Any,
    ) -> Type[T]:
        if "__module__" in namespace or "__qualname__" in namespace:
            del namespace["__module__"]
            del namespace["__qualname__"]

        if "__slots__" in namespace:
            slots = namespace.pop("__slots__")
            attrs = {}
            for attr in slots:
                attr = attr.strip()
                attrs[attr] = TypedDescriptor(TypeVar(attr))
            namespace.update(attrs)

        print(namespace)
        cls = super().__new__(metacls, name, bases, namespace)
        cls._registry = {}
        for base in reversed(bases):
            reg_cls = registry(base)
            if reg_cls:
                reg_cls.register(cls)
        return cls


def registry(target: type) -> Optional[ClassVar[list]]:
    def decorator(cls: type):
        try:
            target._registry.append(cls)
        except AttributeError:
            target._registry = [cls]
        return cls
    return decorator


@contextlib.contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions as e:
        pass


# ─── ApplicationContext ──────────────────────────────────────────────────────

class ApplicationContext(object):

    def __init__(self, *argv, **env):
        self.argv = argv
        self.env = env

    @property
    def args(self):
        return self.argv + list(sys.argv[1:])

    @property
    def kwargs(self):
        env = {
            k: v
            for k, v in self.env.items() 
            if k.startswith("_") and (v := os.environ.get(k)) != None
        }
        return {k.replace("_", "-"): v for k, v in env.items()}

    def get_env(self, key):
        return self.kwargs[key]

    def set_env(self, key, value):
        return self.kwargs.setdefault(key, value)

    def run(self, func):
        with suppress(KeyboardInterrupt):
            func(**self.kwargs)



# ─── ContextManager ──────────────────────────────────────────────────────────

class MyContextManager:

    def __enter__(self):
        return "Entered"

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True