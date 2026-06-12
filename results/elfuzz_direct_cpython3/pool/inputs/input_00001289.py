"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result

# ── Currying & Partial Application ────────────────────────────────────────────

def curry(fn, *args, depth=2, **kwargs):  
    """
    Curry a function by one argument at a time.
    
    Parameters
    ----------
    fn : Callable[..., T]
        The function to be curried
    args : tuple[Any], optional
        Initial arguments, by default ()
    depth : int, optional
        Number of additional arguments to curry, by default 2
    kwargs : dict[str, Any], optional
        Additional keyword arguments, by default {}

    Returns
    -------
    Callable[..., T]
        A new function with the first N arguments already filled
    """

    @functools.wraps(fn)
    def wrapper(*inner_args, **inner_kwargs):
        nonlocal depth
        inner_args += args
        inner_kwargs.update(kwargs)

        if len(inner_args) >= depth:
            return fn(*inner_args, **inner_kwargs)

        return lambda *more_inner_args, **more_inner_kwargs: curry(
            fn,
            *inner_args,
            *more_inner_args,
            depth=depth,
            **inner_kwargs,
            **more_inner_kwargs,
        )

    return wrapper


def partial_apply(fn, *args, **kwargs):
    """
    Create a partially applied copy of a function.

    The returned function will take any remaining arguments and call `fn`
    with all the provided ones plus those specified here.

    Parameters
    ----------
    fn : Callable[..., T]
        A function to partially apply
    args : tuple[Any], optional
        Positional arguments to supply to `fn`, by default ()
    kwargs : dict[str, Any], optional
        Keyword arguments to supply to `fn`, by default {}

    Returns
    -------
    Callable[..., T]
        A copy of `fn` supplied with some initial positional or keyword
        arguments
    """
    return lambda *a, **k: fn(*(list(args) + list(a)), **dict(kwargs, **k))


# ── Currying an outer-curried function ───────────────────────────────────────

def curry2(fn, *args, depth=2, **kwargs):
    return curry(curry(fn, *args, depth=depth, **kwargs), depth=depth, **kwargs)


# ── Trampoline (tail-call optimisation) ──────────────────────────────────────

def trampoline(func: Callable[P, A          __class_getitem__, __set_name__, __init_subclass__,
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
import re
import shutil
import subprocess
import traceback
import types
import uuid
import warnings
from abc import ABCMeta, abstractmethod
from collections import UserDict, defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from functools import lru_cache, wraps
from heapq import merge
from inspect import (
    ArgSpec,
    BoundArguments,
    isbuiltin,
    isclass,
    isfunction,
    signature,
    Signature,
)
from ipaddress import IPv4Address, IPv6Address, ip_address
from itertools import chain, combinations, count, cycle, dropwhile, filterfalse, groupby
from itertools import islice, permutations, product, repeat, starmap, takewhile, tee
from json.decoder import JSONDecodeError
from math import ceil, copysign, degrees, factorial, floor, hypot, inf, lcm, log, pi, sin
from mimetypes import guess_type
from operator import itemgetter, methodcaller
from pkgutil import extend_path
from random import choice, choices, randbytes, randint, randrange, sample, shuffle, seed
from string import ascii_letters, digits
from threading import Lock
from timeit import Timer
from typing import Any, ClassVar, Literal, NamedTuple, NoReturn, Optional, Protocol, TypedDict
from unicodedata import category, normalize, east_asian_width
from weakref import ref, WeakKeyDictionary, WeakSet

MAXFLOAT = float('inf')
MINUS_INFINITY = -float('inf')
POSITIVE_INFINITY = float('inf')

"""Python 3.8+

Optional[T]       | Type[typing.Optional[T]]     | Union[tuple(None, T)]
"""


def sort_by_key(iterable: Iterable[A], key_func: Callable[[Any], Any]) -> Iterator[A]:
    """Sort iterable using key_func"""
    return sorted(iterable, key=key_func)


@dataclass(order=True, frozen=False)
class Person:
    name: str
    age: int
    gender: str
    address: Address


@dataclass(order=True)
class Address:
    street: str
    city: str
    state: str


def sort_people(people: List[Person]):
    people.sort(key=lambda p: p.age)


def match_person(person: Person):
    match person:
        case {"address": {"city": city, "state": state}, "name": name} if len(name)        raise ValueError(f"No case matched on {value}")
    return default


person = {
    "name": "Mickey",
    "age": 45,
    "gender": "Male",
    "address": {"street": "Main St.", "city": "San Francisco", "state": "CA"},
}

match person:
    case {"name": name, "age": age} as p if age > 18:
        print(p.name)
    case {"name            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn


def make_adder_from_bytecode(delta: int) -> types.FunctionType:
    """Build a function entirely from a code object (LOAD_FAST + LOAD_CONST + BINARY_OP + RETURN)."""
