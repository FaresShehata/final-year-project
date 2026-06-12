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


def zero(n: int) -> bool:
    return n == 0


def succ(n: int) -> int:
    return n + 1


def pred(n: int) -> int:
    return n - 1 if n > 0 else 0


def iszero(n: int) -> bool:
    return IF(zero, FALSE, TRUE)(n)


def nat_successor(x: int | str) -> int | str:
    match x:
        case int() as y:
            return succ(y)

        case str() as y:
            return str(succ(int(y)))


def nat_predecessor(x: int | str) -> int | str:
    match x:
        case int() as y:
            return pred(y)

        case str() as y:
            return str(pred(int(y)))


def zero_to_nat(x: int) -> str:
    return "0" * x


def nat_to_zero(x: str) -> int:
    return len(x)


def nat_natural(x: int) -> str:
    return str(x)


def nat_add(x: str, y: str) -> str:
    return zero_to_nat(nat_predecessor(nat_to_zero(x)) + nat_to_zero(y))


def nat_subtract(x: str, y: str) -> str:
    return nat_to_zero(x) - nat_to_zero(y)


def nat_multiply(x: str, y: str) -> str:
    return zero_to_nat(
        int(nat_to_zero(x))
        - int(0)
        + int(nat_to_zero(y))
        - int(0)
        + int(nat_to_zero(x))
        - int(nat_to_zero(y))
        - int(2)
    )


def nat_divide(x: str, y: str) -> str:
    return nat_to_zero(nat_add(nat_to_zero(x), nat_to_zero(nat_predecessor(y)))) // 2


def nat_modulo(x: str, y: str) -> str:
    return nat_to_zero(nat_add(nat_to_zero(x), nat_to_zero(nat_predecessor(y)))) % 2


def nat_less_than(x: str, y: str) -> str:
    return IF(zero_to_nat(nat_subtract(y, x)), TRUE, FALSE)(x)


def nat_greater_than(x: str, y: str) -> str:
    return NOT(nat_less_than(y, x))

# ─
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
    Iterable,
    List,
    Literal,
    NoReturn,
    NewType,
    NamedTuple,
    Optional,
    Protocol,
    Tuple,
    TypeAlias,
    TypeGuard,
    TypedDict,
    Union,
    get_args,
    get_origin,
    get_origin,
    get_type_hints,
)
from typing_extensions import (
    Concatenate,
    ConcatenateGeneric,
    ParamSpec,
    ConcatenateOptional,
    ConcatenateRequired,
    ConcatenateUnpack,
    ConcatenateExtra,
    ConcatenatePartial,
    ConcatenateSubtype,
    ConcatenateMixin,
    ConcatenateEmpty,
    ConcatenateFinal,
    ConcatenatePartialFinal,
    ConcatenateSubtypeFinal,
    ConcatenateMixinFinal,
    ConcatenateEmptyFinal,
    ConcatenateFinalFinal,
    ConcatenatePartialFinalFinal,
    ConcatenateSubtypeFinalFinal,
    ConcatenateMixinFinalFinal,
    ConcatenateEmptyFinalFinal,
    ConcatenateFinalFinalFinal,
    ConcatenatePartialFinalFinalFinal,
    ConcatenateSubtypeFinalFinalFinal,
    ConcatenateMixinFinalFinalFinal,
    ConcatenateEmptyFinalFinalFinal,
    ConcatenateFinalFinalFinalFinal,
    ConcatenatePartialFinalFinalFinalFinal,
    ConcatenateSubtypeFinalFinalFinalFinal,
    ConcatenateMixinFinalFinalFinalFinal,
    ConcatenateEmptyFinalFinalFinalFinal,
    ConcatenateFinalFinalFinalFinalFinal,
    ConcatenatePartialFinalFinalFinalFinalFinal,
    ConcatenateSubtypeFinalFinalFinalFinalFinal,
    ConcatenateMixinFinalFinalFinalFinalFinal,
    ConcatenateEmptyFinalFinalFinalFinalFinal,
    ConcatenateFinalFinalFinalFinalFinalFinal,
    ConcatenatePartialFinalFinalFinalFinalFinalFinal,
    ConcatenateSubtypeFinalFinalFinalFinalFinalFinal,
    ConcatenateMixinFinalFinalFinalFinalFinalFinal,
    ConcatenateEmptyFinalFinalFinalFinalFinalFinal,
    ConcatenateFinalFinalFinalFinalFinalFinalFinal,
    ConcatenatePartialFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateSubtypeFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateMixinFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateEmptyFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateFinalFinalFinalFinalFinalFinalFinalFinal,
    ConcatenatePartialFinalFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateSubtypeFinalFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateMixinFinalFinalFinalFinalFinalFinalFinalFinal,
    ConcatenateEmptyFinalFinalFinalFinalFinal