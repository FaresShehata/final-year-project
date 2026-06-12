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
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
import types
import zipfile as zip_mod
from collections.abc import Callable, Iterator
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timedelta
from functools import partialmethod, wraps
from itertools import chain, product
from math import ceil, gcd as _gcd, log2, prod
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import randint
from string import Formatter as Formatter_cls
from tokenize import TokenInfo
from typing import (
    Any, BinaryIO, ClassVar, Dict, Generic, Iterable, List, Literal, Mapping,
    MutableMapping, Match, Optional, Pattern, Tuple, TypedDict, TypeVar,
    Union, cast, overload
)
from typing_extensions import Final, Protocol, runtime_checkable, Concatenate
from uuid import UUID

if sys.version_info >= (3, 9): from collections.abc import AsyncGenerator, Awaitable
else:                           from async_generator import asynccontextmanager as asynccontextmanager
from concurrent.futures import ThreadPoolExecutor as FuturePool
from contextlib import suppress, redirect_stdout, AbstractContextManager
from contextvars import ContextVar
from pathlib import Path
from tempfile import TemporaryDirectory
from typing_extensions import get_args, get_origin, get_type_hints, get_origin, get_args, get_origin
from numbers import Integral
from contextlib import contextmanager
from contextvars import ContextVar
from enum import EnumMeta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import _eval_type, _type_vars, _make_class_def, TypeGuard, _eval_type, _type_vars, _make_class_def
from numbers import Integral
from contextlib import contextmanager
from enum import EnumMeta
from pathlib import Path
from tempfile import TemporaryDirectory
from abc import abstractmethod
from decimal import Decimal
from typing import Protocol, runtime_checkable, runtime_checkable, runtime_checkable, runtime_checkable



# ── Custom types ─────────────────────────────────────────────────────────────

def _parse_typeddict(typ: type[_T]):
    typ_var, attrs = _type_vars(typ).pop()
    return typ_var, attrs

_T = TypeVar('_T')

@runtime_checkable
class _Iterable(TypedDict):
    __mro_entries__: tuple[type[_T], ...]


@runtime_checkable

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
