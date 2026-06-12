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
import os.path as path
import re
import shutil
import signal
import string
import struct
import sys
import time
import types
import typing
import unittest.mock
import warnings
import weakref
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from functools import partial, wraps
from itertools import zip_longest
from pathlib import Path
from pprint import pprint
from threading import Thread
from tokenize import TokenInfo, tokenize
from typing import (
    Any, ClassVar, Dict, Hashable, ItemsView, Iterable, Iterator, KeysView,
    List, Mapping, Optional, Sequence, Tuple, Type, Union, ValuesView
)
from urllib.parse import urlparse
from uuid import uuid4
from xml.etree.ElementTree import Element, fromstring, parse
from zipfile import ZipFile


# ── typing extras ────────────────────────────────────────────────────────────

# https://docs.python.org/3/library/typing.html#typing.TypeAlias
# https://github.com/python/typing/issues/789
TypeAlias = TypeVar("TypeAlias")

# https://docs.python.org/3/library/typing.html#typing.ParamSpec
ParamSpec = TypeVar("ParamSpec", bound=types.GenericAlias)

# https://docs.python.org/3/library/typing.html#typing.Concatenate
Concatenate = TypeVar("Concatenate")

# https://github.com/python/typing/pull/1641
Annotated = TypeVar("Annotated")

# https://peps.python.org/pep-0586/#raise-type-hint-inference
Never = TypeAlias("Never") = object()

# https://github.com/python/typing/pull/1641
Annotated = TypeVar("Annotated")

# https://peps.python.org/pep-0586/#raise-type-hint-inference
reveal_type = TypeVar("reveal_type")


# ── collections.abc ─────────────────────────────────────────────────────────

class ItemsView(MutableMapping[Tuple[K, V], V]):
    """Dictionary view of a dictionary-like mapping."""


# ── concurrent.futures ───────────────────────────────────────────────────────

class Future(typing.Protocol):

    def done(self) -> bool: ...       # pylint: disable=E1136,E1125
    def cancel(self) -> bool: ...     # pylint: disable=E1    throughput: float
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
