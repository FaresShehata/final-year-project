"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import inspect
import itertools
import operator
import os
import pathlib
import pickle
import random
import re
import string
import typing as t
import weakref
from collections.abc import (
    Awaitable,
    Callable,
    Collection,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Set,
    MutableMapping,
)
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime, timedelta
from enum import Enum, auto, unique
from enum import (
    IntEnum,
    IntFlag,
    IntDescriptionMixin,
    StrEnum,
    ReprEnum,
    IntFlags,
)
from enum_tools import EnumMeta
from enum_tools.enum_tools import EnumToolsMeta
from enum_tools.repr_enum import ReprEnumMeta


def _get_json_encoder_class() -> type[json.JSONEncoder]:
    """Get the JSON encoder class."""
    try:
        from json.encoder import JSONEncoder

        return JSONEncoder
    except ImportError:
        pass

    try:
        from jsonlib.jsonencoder import JSONEncoder

        return JSONEncoder
    except ImportError:
        pass

    raise RuntimeError("No JSON encoder found.")


JSONEncoderType = t.TypeVar("JSONEncoderType", bound=type[_get_json_encoder_class()])


def get_json_encoder() -> JSONEncoderType:
    """Get a serializable JSON encoder for all classes in this module."""
    return _get_json_encoder_class()


@t.overload
def is_iter(obj: None | Collection[t.Any]) -> bool: ...


# @overload
def is_iter(obj: Any) -> bool: ...
...

is_iter = lambda obj: hasattr(obj, "__iter__")


def is_collection(obj: object) -> bool:
    """
    Return True if `obj` is an instance of a collection,
    else returns False.
    """

    # TODO: Add support for custom collections?

    return isinstance(obj, (list, tuple, set)) or hasattr(obj, "__getitem__")


def has_attr(obj: object, name: str) -> bool:
    """Return True if `obj` has an attribute with the given `name`, else returns False."""

    return hasattr(obj, name)


def is_weakref(obj: object) -> bool:
    """Return True if `obj` is a weak reference to another object, else returns False."""

    return isinstance(obj, weakref.ref)


def is_callable(obj: object) -> bool:
    """Return True if `obj` can be called, else returns False."""

    return callable(obj)


def is_instance_of(obj: object, cls: type) -> bool:
    """Return True if `obj` is an instance of `cls`, else returns False."""

    return isinstance(obj, cls)


def is_subclass(cls: type, base_cls: type) -> bool:
    """Return True if `cls` is a subclass of `base_cls`, else returns False."""

    return issubclass(cls, base_cls)


def is_mixin(cls: type) -> bool:
    """Return True if `cls` is a mixin class, else returns False."""

    return cls.__bases__[0].__name__.endswith("_mixin")


def is_singleton(cls: type) -> bool:
    """Return True if `cls` is a singleton class, else returns False."""

    return issubclass(cls, Singleton)


def is_context_manager(cls: type) -> bool:
    """Return True if `cls` implements the ContextManager protocol, else returns False."""

    return inspect.iscontextmanager(cls)


def is_generator_function(func: Callable[..., Any]) -> bool:
    """Return True if `func` is a generator function, else returns False."""

    return inspect.isgeneratorfunction(func)


def is_async_generator_function(func: Callable[..., Any]) -> bool:
    """Return True if `func` is an asynchronous generator function, else returns False."""

    return inspect.isasyncgenfunction(func)


def is_async_gen(gen: AsyncGenerator[Any, Any]) -> bool:
    """Return True if `gen` is an asynchronous generator object, else returns False."""

    return inspect.isasyncgenobject(gen)


def is_coroutine(coro: Coroutine[Any, Any, Any]) -> bool:
    """Return True if `coro` is a coroutine object, else returns False."""

    return inspect.iscoroutine(coro)


def is_metadata_type(obj: object) -> bool:
    """Return True if `obj` is a metadata type, else returns False."""

    return isinstance(obj, MetadataType)


def is_metaclass(metaclass: type) -> bool:
    """Return True if `metaclass` is a metaclass, else returns False."""

    return inspect.isabstract
def get_attribute(obj: object, name: str) -> Any:
    """Return the value of the attribute `name` on `obj`.

    Raises AttributeError if the attribute does not exist.

    >>> get_attribute(Person(first_name="John"), "first_name")
    'John'

    >>> get_attribute(Person(first_name="John"), "age")
    Traceback (most recent call last):
      ...
    AttributeError: Person has no attribute named age.
    """

    if not has_attr(obj, name):
        raise AttributeError(f"{obj.__class__.__qualname__} has no attribute named {name}.")
    return getattr(obj, name)


def set_attribute(obj: object, name: str, value: Any) -> None:
    """Set the value of the attribute `name` on `obj`.

    If the attribute does not exist, it will be created.
    """

    if not has_attr(obj, name):
        setattr(obj, name, value)
    elif isinstance(getattr(obj, name), property):  # noqa: PLR2004
        # The        return cls(
            task_id,
            task_name,
            Priority(task_priority),
            Status(d["status"]),
            task_tags,
            task_metadata,
            default_priority=default_priority,
        )


@dataclasses.dataclass
class Person:
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float
    description: str = ""
    email_addresses: frozenset[str] = dataclasses.field(default_factory=frozenset)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}: {self.first_name}, {self.age}, {self.gender}"

