"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

JsonDict: TypedDict["JsonDict", str: JsonValue]


def json_parse(json_str: str) -> JsonDict:
    assert isinstance(json_str, str), repr(json_str)
    return ast.literal_eval(json_str) # type: ignore


# ── Enumerations ─────────────────────────────────────────────────────────────

class Fields(NamedTuple): 
    x: int
    y: int


_fields = Fields(1, 2)

assert _fields.x == 1
assert _fields.y == 2


@dataclasses.dataclass(frozen=True)
class PointN:
    x: int
    y: int


pointn_1 = PointN(3, 4)

assert pointn_1.x == 3
assert pointn_1.y == 4


class PointM(Generic[int, int]): 
    x: int
    y: int 


pointm_1 = PointM(5, 6)

assert pointm_1.x == 5
assert pointm_1.y == 6


class EvenPoint(PointN): 
    ...


even_point_2 = EvenPoint(7, 8)

assert even_point_2.x == 7
assert even_point_2.y == 8


# ── Decorators ──────────────────────────────────────────────────────────────

def is_finite_number(x: float) -> Predicate[float]: 
    ...


# ── Functions ───────────────────────────────────────────────────────────────

def add(a: int, b: int) -> int:
    return a + b


def process_slice(slice_args: slice) -> Tuple[Any, ...]:
    start, stop, step = slice_args.indices(len(obj)) # type: ignore
    return obj[start:stop:step]


def do_work(item: T) -> T:
    ...


def sequence_step(
    iterable: Sequence[T],
    predicate: Predicate[T],
    func: Callable[..., T],
) -> Generator[T, None, None]:

    for item in iterable:
        if predicate(item):
            yield item # type: ignore
        else:
            next_item = func(item)
            yield from sequence_step(iterable[next_item:], predicate, func)


class Fields(NamedTuple): 
    x: int
    y: int


def fields_from_slice(slice_args: slice) -> Fields:
    start, stop, step = slice_args.indices(len(obj)) # type: ignore
    return

class NeedsInstanceType(_Annotated[_T]):
    """The annotated object must be of a specific class."""

    def __new__(cls, *args, **kwargs):
        cls.__concrete__ = True
        return super().__new__(cls, *args, **kwargs)


class HasName(_Annotated[str]):
    """The annotated object has a specific name."""

    def __new__(cls, *args, **kwargs):
        cls.__concrete__ = True
        return super().__new__(cls, *args, **kwargs)


class Annotated[T]:
    """A descriptor with type-hinted value and constraints.

    Constraints are described by `Constraint` sub-types.
    """

    _constrs: tuple[type[Constraint], ...]
    _name_:  str

    def __init__(
        self,
        t:              type[T],
        constrs:        Iterable[type[Constraint]] = (),
        *,
        name:           Optional[str] = None,
        extra_typeshed: bool              = False,
    ):
        self._constrs = tuple(constrs)
        self._name_   = name or t.__name__
        if extra_typeshed:
            self.__annotations__[self._name_] = t

