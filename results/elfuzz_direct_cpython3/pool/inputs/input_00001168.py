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


JSONEncoderType = t.TypeVar("JSONEncoderType", bound=t.Type[_get_json_encoder_class()])


class CustomJSONEncoder(_get_json_encoder_class()):
    """Custom JSON encoder."""

    def default(self, o) -> t.Any:
        if hasattr(o, "__dict__"):
            return vars(o)
        else:
            return super().default(o)


# https://stackoverflow.com/a/38739695
class MyDataClass(dataclasses.Dataclass):

    @classmethod
    def fields(cls) -> tuple[dataclasses.Field, ...]:
        return dataclasses.fields(cls)

    @classmethod
    def defaults(cls) -> dict[str, t.Any]:
        return {
            attr.name: getattr(cls(), attr.name) for attr in cls.fields() if attr.default is not dataclasses.MISSING
        }


@unique
class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()


@unique
class TaskPriority(IntFlag):
    LOWEST = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    HIGHEST = auto()


@dataclass(slots=True, frozen=False)
class TaskReport:

    task_id: str
    task_name: str
    priority: TaskPriority
    status: TaskStatus
    tags: FrozenSet[str]
    metadata: dict[str, t.Any]


@dataclasses.dataclass(slots=True, frozen=False)
class TaskInfo:

    task_id: str
    task_name: str
    priority: TaskPriority
    status: TaskStatus
    tags: FrozenSet[str]
    metadata: dict[str, t.Any]

    @staticmethod
    def from_dict(d: dict[str, t.Any]) -> TaskInfo:
        return TaskInfo(**d)

    def to_dict(self) -> dict[str, t.Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(slots=True, frozen=False)
class TaskResult(TaskInfo):

    output_file_path: pathlib.Path | None = dataclasses.field(init=False, compare=False, default=None)

    @property
    def output_file_path_str(self) -> str | None:
        if self.output_file_path is None:
            return None
        return self.output_file_path.resolve().__str__()

    def save_output_file(self, file_path: pathlib.Path | None = None) -> None:
        if file_path is None and self.output_file_path is not None:
            file_path = self.output    >>> get_attribute(Person(first_name="John"), "first_name")
    'John'

    >>> get_attribute(Person(first_name="John"), "age")
    Traceback (most recent call last):
      ...
    AttributeError: Person has no attribute named age.
    """

    if not has_attr(obj, name):
        raise AttributeError(f"{obj.__class__.__qualname__} has no attribute named {name}.")
    return getattr(obj, name)


def set_attribute(
    obj: object,
    name: str,
    value: t.Any,
    *,
    create_if_missing: bool = False,
    force_frozen: bool = True,
    **kwargs: t.Any,
) -> None:
    """
    Set an attribute on an object.

    Raises `AttributeError` if the attribute does not exist or cannot be set.

    Args:
        obj: The object to set the attribute on.
        name: The name of the attribute to set.
        value: The value to set the attribute to.
        create_if_missing: If the attribute does not exist and this flag is set to true, it will be created with
            a default value. Otherwise, an `AttributeError` will be raised.
        force_frozen: If the attribute exists but is frozen, this flag can be used to make it unfrozen before setting
            the new value. This is useful when the attribute is read-only, e.g., a property that should be writable.
    """
    if not has_attr(obj, name):
        if create_if_missing:
            setattr(obj, name, value)
        else:
            raise AttributeError(f"{obj.__class__.__qualname__} has no attribute named {name}.")
    else:
        if force_frozen and getattr(obj, name).frozen:
            setattr(obj, name, value)
    <|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>    elif isinstance(getattr(obj, name), property):  # noqa: PLR2004
