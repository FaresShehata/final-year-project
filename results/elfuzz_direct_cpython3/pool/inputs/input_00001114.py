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

T  = TypeVar("T"), K, V, K1, K2, A, B, C, D, E, F, G, H, I, J, X, Y, Z, S, T, U, V, W, X, Y, Z, L, M, N, O, P, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R, S, T, U, V, W, X, Y, Z, Q, R, S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z, Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U, V, W, X, Y, Z ,Q, R ,S, T, U
assert all([
    True == is_true(TRUE(True)),
    False == is_true(FALSE(False))
])

zero   = lambda n: FALSE()
succ   = lambda n: lambda f: lambda x: n(f)(f(x))
pred   = lambda n: lambda z: n(lambda u: lambda v: v(u(z)))
add    = lambda m: lambda n: lambda s: lambda z: m(succ(n))(lambda y: pred(y)(z))
mult   = add(mult)
exp    = mult(exp)
div    = lambda m: lambda n: n(div(m))

assert all([
    zero(0),
    succ(zero)(0),
    pred(succ(pred(zero)))(0),

    add(one)(one)(two)(three)(four)(five)(six)(seven)(eight)(nine)(ten)(eleven)(twelve)(
        thirteen)(fourteen)(fifteen)(sixteen)(seventeen)(eighteen)(nineteen)(twenty)
])


assert all([
    one + one == two,
    three - one == two,
    four * two == six,
    five / two == two,

    exp(two)(three) == eight,
    div(three)(two) == one,
    div(eight)(two) == four
])

# ─── Higher-order functions and function composition ────────────────────────


def map(func: Callable[[Any], B], seq: list[A]) -> list[B]:
    """Returns a sequence with the elements of `seq` mapped with `func`.

    This function does not modify the original sequence.
    """
    result = []
    for item in seq:
        result.append(func(item))

    return result


def filter(predicate: Callable[[Any], bool], seq: list[Any]) -> list[Any]:
    """Filters out items of `seq` according to `predicate`, returning only those that satisfy it.

    This function does not modify the original sequence.
    """
    result = []
    for item in seq:
        if predicate(item):
            result.append(item)

    return result


