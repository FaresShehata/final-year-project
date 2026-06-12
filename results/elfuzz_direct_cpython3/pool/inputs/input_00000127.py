"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
───────────────────────────────────────────────────────────────────────────────

- Use the `numbers` abstract base types.
- Use the `pathlib` module.
- Use the `tempfile`, `csv`, `base64`, `hashlib`, `hmac`, `secrets`
  modules.

"""
from collections.abc import Iterable, Callable
from dataclasses import dataclass, field
import enum
import functools
from itertools import chain, cycle, tee
from operator import itemgetter
import os.path
import re
import sys
import threading
import time
from typing import (
    Any, Generic, List, Sequence, Tuple, Set, Optional, Dict, Union, NamedTuple,
    Generator, Protocol, ClassVar, TypeVar, runtime_checkable, cast,
    TYPE_CHECKING
)
from typing_extensions import TypeGuard, final, Self
from typing import TextIO as IO_Type
from urllib.parse import quote as urlquote
from uuid import UUID

impoimt "typing_extensions"
from typing_extensions import get_args, get_origin, get_type_hints, Annotated

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

try:
    from mypy_extensions import TypedDict
except ImportError:
    from typing_extensions import TypedDict

# ── Enumerations ──────────────────────────────────────────────────────────────

class State(enum.Enum):
    ERROR = 1    # error state
    OK    = 2    # ok state
    WARN  = 3    # warning state


class Priority(enum.IntEnum):
    CRITICAL      = 10
    IMPORTANT     = 8
    NORMAL        = 5
    LOW           = 2

    @classmethod
    def values(cls) -> Tuple[int, ...]:
        return tuple(sorted(c.value for c in cls))

    @classmethod
    def items(cls) -> List[Tuple[int, str]]:
        return [(c.value, c.name) for c in cls]

    @classmethod
    def names(cls) -> List[str]:
        return [c.name.lower() for c in cls]

    @classmethod
    def iter_items(cls) -> Iterable[Tuple[int, str]]:
        return ((c.value, c.name) for c in cls)


# ── Decorators ────────────────────────────────────────────────────────────────

@final
class TimeElapsedDecorator(Generic[Any]):
    """Decorator that measures elapsed time of a function."""

    def __# ── TypeAlias ────────────────────────────────────────────────────────────────

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
