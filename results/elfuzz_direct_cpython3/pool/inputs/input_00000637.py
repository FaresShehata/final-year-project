"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          dataclasses (order, frozen, slots), generic container (generic class),
          decorators (type annotations, runtime_checkable, overload, no_type_check),
          protocols (protocols), dataclasses (dataclass), generic container (Generic),
          decorators (type annotations, runtime_checkable, overload, no_type_check).
"""

import enum
from collections import namedtuple
from enum import auto
from functools import wraps
from itertools import count
from operator import attrgetter
from pickletools import long1
from random import choice, randint
from re import subn
from time import sleep
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    cast,
)
from typing_extensions import (
    Annotated,
    Concatenate,
    ClassVar,
    Final,
    Generic,
    NoReturn,
    Never,
    ParamSpec,
    TypeAlias,
    TypeGuard,
    TypeVar,
    get_args,
    get_origin,
)
import typing

# TODO: fix with open in unix
# from pathlib import Path
# path = Path(__file__).parent / "seed_04.txt"
# print(path.read_text())


def decorator(func: Callable[..., str]) -> Callable[[Any], int]:
    """Decorator to add a prefix to the output of the function."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> int:
        return len(f"prefix : {func(*args, **kwargs)}") + 16

    return wrapper


@decorator
def seed_03() -> int:
    """A simple seed that returns a number."""
    return 0.123456789


@decorator
def seed_04() -> int:
    """Another simple seed that returns a number."""
    return 1.23456789


print(seed_03())
print(seed_04())


class Seed_05(enum.Enum):
    """
    An enumeration representing different seeds.
    """

    SEED_A = 0.123456789
    SEED_B = 1.23456789
    SEED_C = 2.3456789
    SEED_D = 3.456789
    SEED_E = 4.56789
    SEED_F = 5.6789
    SEED_G = 6.789


# seed_05_dict = {key.name: value.value for key, value in Seed_05.__members__.items()}
# seed_05_list = [key.value for key in Seed_05]
# seed_05_set = set(Seed_05)

# print(type(members))
# print(type(values))
# print(type(lists))

# seed_05_dict = {key.name: value.value for key, value in Seed_05.__members__.items()}