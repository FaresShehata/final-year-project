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

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                match constraint:
                    case ConstraintType.NeedsInstanceType():
                        if not isinstance(value, type(obj)):
                            raise TypeError(
                                f"{value=} should be an instance of {type(obj)}",
                            )
                    case ConstraintType.HasName(name_):
                        if not name_ == obj.name:
                            raise ValueError(f"'{obj}' does not have the '{name_}' name")
                    case _:
                        pass      # no-op
        setattr(obj, self.priv, value)


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

    def __instancecheck__(self, value: object) -> bool:
        return isinstance(value, self.t)

    @property
    def t(self) -> type[T]:
        return self.__annotations__[self._name_]

    def __repr__(self) -> str:
        args = [f"name='{self._name_}'", f"constr={self.constrs}"]
        if len(args) > 1:
            args.append(", ")
        args.extend(repr(arg) for arg in self.extra_args)
        args.append(":")
        return f'{self.type_}{args}'

    def __getattribute__(self, attr):
        try:
            if attr.startswith("_"):
                return