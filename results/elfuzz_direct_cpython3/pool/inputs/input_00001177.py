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

    raise RuntimeError(f"Could not find either 'json' or 'jsonlib.jsonencoder' module.")


JSONEncoderType = _get_json_encoder_class()


class SeedException(Exception):
    """Base exception for all seed exceptions."""


class InvalidConfigValueException(SeedException):
    """Raised when there is a problem parsing a config file."""


class DuplicateNameException(SeedException):
    """Raised when trying to register two types with the same name."""


class NotRegisteredWithMetaclassException(SeedException):
    """Raised when attempting to access a method that requires a registered type."""


@dataclass(slots=True)
class ConfigFileSettings:
    """Configuration settings for a given config file."""

    filename: PathLike | None = None
    separator: str = ":"
    comment_symbol: str = "#"


@dataclass(slots=True)
class ConfigFile:
    """Representation of a config file."""

    path: path.PathLike
    settings: ConfigFileSettings = field(default_factory=ConfigFileSettings)

    def load(self) -> dict[str, str]:
        """Load the contents of this config file into memory."""

        with open(self.path, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        sections: list[list[str]] = []
        section_name = ""
        section_data: list[tuple[str, str]] = []

        for line in lines:
            if line.startswith("#"):
                continue

            if line.startswith("["):
                if len(section_data) > 0:
                    sections.append(section_data.copy())
                    section_name = line.replace("[", "").replace("]", "")
                    section_data.clear()
                else:
                    section_name = line.replace("[", "").replace("]", "")

                continue

            if len(line.split(self.settings.separator)) != 2:
                raise InvalidConfigValueException(
                    f"'{line}' is not a valid key-value pair."
                )

            section_data.append((section_name, line))

        sections.append(section_data.copy())

        configs: dict[str, dict[str, str]] = {}

        for section in sections:
            configs[section[0].lower()] = {k.lower(): v for k, v in section}

        return configs

    @staticmethod
    def load_from_path(path: PathLike, **kwargs: Any) -> ConfigFile:
        """Create a new ConfigFile by loading it from the given path."""

        return ConfigFile(path=path,    Return True if `obj` is an instance of a collection,
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
