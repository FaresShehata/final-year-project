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
    joined_at: Seconds
    last_login:      Optional[Seconds]
    is_superuser:    Optional[bool]


def flatten_dict(dct: dict[str, JsonValue]) -> JsonValue:
    if isinstance(dct.get("children"), dict):
        return flatten_dict(dct["children"])
    elif isinstance(dct.get("children"), list):
        for child in dct["children"]:
            if isinstance(child, dict) and "name" not in child:
                yield from flatten_dict(child)
            else:
                yield child
    else:
        yield dct


# ── ParamSpec ────────────────────────────────────────────────────────────────

def foo(
    x: int,
    y: str,
    z: float,
    /,
    w: list[int],
    a: set[str],
    b: tuple[float, ...],
    c: frozenset[complex],
    d: bytes,
    *args: int,
    e: classmethod,
    f: property,
    g: final,
    h: type[Any],
    i: object,
    j: complex,
    k: range,
    l: slice,
    m: enumerate,
    n: zip,
    o: map,
    p: filter,
    q: reversed,
    r: collections.abc.Iterable[T],
    s: collections.abc.Mapping[str, T],
    t: collections.abc.Sequence[T],
    u: collections.abc.Set[T],
    v: collections.abc.ByteString,
    w: collections.abc.Buffer,
    x: collections.abc.Callable[..., T],
    y: collections.abc.Coroutine[tuple[str, ...], Any, T],
    z: collections.abc.Generator[T, str, None],
    aa: collections.abc.Iterator[T],
    bb: collections.abc.KeysView[str],
    cc: collections.abc.ValuesView[T],
    dd: collections.abc.ItemsView[str, T],
    ee: collections.abc.MutableMapping[str, T],
    ff: collections.abc.MutableSequence[T],
    gg: collections.abc.MutableSet[T],
    hh: collections.abc.Sequence[T],
    ii: collections.abc.Sized,
    jj: collections.abc.Container[T],
    kk: collections.abc.Collection[T],
    ll: collections.abc.Hashable,
    mm: collections.abc.Reversible[T],
    nn: collections.abc.ScalableContainer,
    oo: collections.abc.MutableScalarCollection,
    pp: collections.abc.MutableSet[T],
    qq: collections.abc.MutableMapping[str, T],
    rr: collections.abc.MutableSequence[T],
    ss: collections.abc.MutableSet[T],
    tt: collections.abc.Sequence[T],
    uu: collections.abc.Set[T],
    vv: collections.abc.Tuple[T, ...],
    ww: collections.abc.Dict[str, T],
    xx: collections.abc.OrderedDict[str, T],
    yy: collections.abc.ChainMap[str, T],
    zz: collections.abc.FrozenSet[T],
    aa_: collections.abc.ItemsGenerator[str, T, Tuple[str, T]],
    bb_: collections.abc.ItemsGenerator[T, str, Tuple[T, str]],
) -> JsonValue:

    ...


# ── Context Managers ─────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exceptions: Exception):
    """Suppress the given exceptions.

    >>> with suppress(ZeroDivisionError, TypeError):
    ...     print(1/0) # ZeroDivisionError
    ...     raise ValueError() # TypeError
    ...     print('always prints') # not reached
    ...
    Traceback (most recent call last):
      File "<stdin>", line 2, in <module>
    ZeroDivisionError

    """
    try:
        yield
    except exceptions:
        pass


@contextlib.contextmanager
def redirect_stdout(stream: io.TextIOBase):
    original_stdout = sys.stdout
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = original_stdout


@contextlib.contextmanager
def abstract():
    """

    >>> with abstract():
    ...     raise NotImplementedError()
    Traceback (most recent call last):
      File "<stdin>", line 3, in <module>
    NotImplementedError

    """
    raise NotImplementedError()


# ── Numbers ABC ──────────────────────────────────────────────────────────────

a = 1_0