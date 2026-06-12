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
    hh: collections.abc.MutableBag[T],
    ii: collections.abc.MutableMapping[str, T],
    jj: collections.abc.MutableMapping[str, T],
    kk: collections.abc.MutableMapping[str, T],
    ll: collections.abc.MutableMapping[str, T],
    mm: collections.abc.MutableMapping[str, T],
    nn: collections.abc.MutableMapping[str, T],
    oo: collections.abc.MutableMapping[str, T],
    pp: collections.abc.MutableMapping[str, T],
    qq: collections.abc.MutableMapping[str, T],
    rr: collections.abc.MutableMapping[str, T],
    ss: collections.abc.MutableMapping[str, T],
    tt: collections.abc.MutableMapping[str, T],
    uu: collections.abc.MutableMapping[str, T],
    vv: collections.abc.MutableMapping[str, T],
    ww: collections.abc.MutableMapping[str, T],
    xx: collections.abc.MutableMapping[str, T],
    yy: collections.abc.MutableMapping[str, T],
    zz: collections.abc.MutableMapping[str, T],
    aaa: collections.abc.MutableMapping[str, T],
    bbb: collections.abc.MutableMapping[str, T],
    ccc: collections.abc.MutableMapping[str, T],
    ddd: collections.abc.MutableMapping[str, T],
    eee: collections.abc.MutableMapping[str, T],
    fff: collections.abc.MutableMapping[str, T],
    ggg: collections.abc.MutableMapping[str, T],
    hhh: collections.abc.MutableMapping[str, T],
    iii: collections.abc.MutableMapping[str, T],
    jjj: collections.abc.MutableMapping[str, T],
    kkk: collections.abc.MutableMapping[str, T],
    lll: collections.abc.MutableMapping[str, T],
    mmm: collections.abc.MutableMapping[str, T],
    nnn: collections.abc.MutableMapping[str, T],
    ooo: collections.abc.MutableMapping[str, T],
    ppp: collections.abc.MutableMapping[str, T],
    qqq: collections.abc.MutableMapping[str, T],
    rrr: collections.abc.MutableMapping[str, T],
    sss: collections.abc.MutableMapping[str, T],
    ttt: collections.abc.MutableMapping[str, T],
    uuu: collections.abc