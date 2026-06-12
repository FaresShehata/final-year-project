"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          struct/union types (NamedTuple, Union, Optional, Literal),
          typing protocols (Protocol, runtime checked with issubclass),
          typing dataclasses (dataclasses, field, frozen),
          private attributes (PrivateAttr, dataclasses.field),
          dataclasses slots (slots, slots=True, asdict, replace),
          dataclasses fields (field, default_factory, init_args, repr_args,
                              eq_attrs, order_attrs, hash_attrs, kw_only,
                              injectable, kw_only_init, naively_annotated,
                              post_init_func, namespace, metadata, compare_fields,
                              compare_attrs, compare_attrs_with_subfields,
                              private_attr, field_set, field_del, field_post_init,
                              field_replace, field_union, field_optional,
                              private_field))
"""

from collections.abc import Callable, Mapping
import contextlib
import inspect
import itertools
import operator
import random
import re
import sys
import timeit
import types
import warnings
import weakref
from functools import partial
from math import gcd as _gcd
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    ByteString,
    ClassVar,
    ContextManager,
    Coroutine,
    Generic,
    Iterator,
    NoReturn,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
    overload_any,
)
from typing_extensions import Annotated, Final, Literal, ParamSpec, Protocol, Self, TypeGuard, TypedDict, get_args, get_origin, get_type_hints, get_type_hints_from_call
from typing_inspect import is_generic_type, is_typeddict

if TYPE_CHECKING or False:
    from typing_extensions import NotRequired, Unpack
else:
    from mypy_extensions import TypedDict, NotRequired, Unpack


# ── Python standard library ──────────────────────────────────────────────────

warnings.filterwarnings(action="ignore", message=".*str object has no .*method?.*")

try:
    import cProfile as Profile
except ImportError:
    import profile as Profile

from multiprocessing import Pool as MultiprocessPool

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait, ALL_COMPLETED
from enum import Enum
from io import StringIO
from itertools import chain, tee
from logging import NullHandler
from os import linesep
from pathlib import Path
from pprint import PrettyPrinter, pformat, pprint, squote
from signal import Signals
from subprocess import    Never,
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
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
    label:   Annotated[str,   short_str] = _Constrained()  # type: ignore[assignment]

    def __init__(self, label: str, reading: float):
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
        return max(0, min(self.end, other.end) - max(self.start, other.start))


# ── numbers ABC ──────────────────────────────────────────────────────────────

class Rational(numbers.Rational):
    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
