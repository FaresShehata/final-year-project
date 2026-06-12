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


def get_first_item(lst: list[Any], default: Any = None) -> Any:
    """
    Return the first item in the given `lst`.
    If the `lst` is empty, return the `default` value.
    """

    return lst[0] if len(lst) > 0 else default


def get_last_item(lst: list[Any], default: Any = None) -> Any:
    """
    Return the last item in the given `lst`.
    If the `lst` is empty, return the `default` value.
    """

    return lst[-1] if len(lst) > 0 else default


def get_random_item(
    lst: list[Any],
    random_source: RandomSource = random.Random(),
    default: Any = None,
    weighted: bool = False,
) -> Any:
    """
    Return a random item from the given `lst`.

    The returned item will be chosen with equal probability.

    Args:
        lst: List to select from.
        random_source: Seed source to use for generating random numbers.
            Defaults to ``random.Random()``
        default: Value to return if `lst` is empty.
        weighted: Whether or not to choose items based on their weights.

    Returns:
        A random item from `lst`. If `lst` is empty and no `default` was provided,
        then raises ``IndexError``.
    """

    if weighted:
        # NOTE: This would actually work correctly if we had a proper weight map...
        if len(lst) == 0:
            raise IndexError("Cannot draw randomly from an empty list")

        if len(lst) == 1:
            return lst[0]

        total_weight = sum(w for _, w in lst)
        rand_num = random_source.random() * total_weight

        current_weight = 0
        for i, (_, w) in enumerate(lst):
            current_weight += w
            if rand_num <= current_weight:
                return lst[i][0]
    else:
        if len(lst) == 0:
            return default

        return lst[random_source.randint(0, len(lst) - 1)]


def mean(*args: Any) -> float:
    """Calculate the arithmetic mean of the given arguments."""
    return sum(args) / len(args)


def median(*args: Any) -> float:
    """Calculate the median of the given arguments."""
    sorted_args = sorted(args)
    mid_idx = (len(sorted_args) + 1) //        )


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

