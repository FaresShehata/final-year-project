"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
import uuid
from collections import deque
from functools import partial
from itertools import chain, count, cycle, islice, zip_longest
from math import ceil, floor, log2
from numbers import Number
from pathlib import Path
from statistics import median
from types import ModuleType
from typing import (
    Any,
    AsyncIterator,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    FrozenSet,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)


# ──────────── Types ────────────────────────────────────────────────────────────────


class Bool(enum.Enum):
    True_ = 1
    False = 0


TRUE  = Bool.True_
FALSE = Bool.False_

AND   = lambda f: lambda g: lambda x: f(x)(g(x))   # λf.λg.λx.f(x)(g(x))
OR    = lambda f: lambda g: lambda x: f(x)(lambda _: g(x)) # λf.λg.λx.f(x)(λy.g(x))

NAND  = FALSE(AND(FALSE))
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>NOT    = FALSE(AND(TRUE(FALSE)))  # λx.x(x)(λy.y)

IF     = OR(lambda c: AND(c(TRUE)))(FALSE(OR(FALSE)))
CONTRU = TRUE(IF)                  # λp.p(true)(false)
CONJ   = AND(CONTRU)               # λp.p(true)(true)
DISJO  = OR(CONTRU)                # λp.p(false)(true)

K      = lambda x: lambda y: x     # λx.λy.x
I      = lambda x: lambda y: x(y)  # λx.λy.x(y)

Y      = I(K(I))(I)                 # λf.(λx.f(xx))(λx.f(xx))
FIX    = Y(Y)                       # λy.y(y)


def bool_to_int(value: bool | None) -> int:
    return bool(value)


def bool_or_bools(bools: Iterable[bool]) -> bool:
    return bool(sum(bools))


def bool_and_bools(bools: Iterable[bool]) -> bool:
    return all(bools)


def bool_not_bool(bool_: bool) -> bool:
    return not bool_


def bool_xor_bools(bools: Iterable[bool]) -> bool:
    return bool_or_bools(bools) ^ bool_and_bools(bools)


def bool_implies_bools(bools: Iterable[bool], inclusive: bool = False) -> bool:
    if len(bools) == 1:
        return bools[0] or not inclusive
    elif len(bools) == 2:
        return bools[0] and (not bools[1] or inclusive)
    else:
        raise ValueError(f"Expected at most two booleans, got {len(bools)}")


def bool_iff_bools(bools: Iterable[bool], inclusive: bool = False) -> bool:
    return bool_implies_bools(bools, inclusive) and bool_implies_bools(reversed(list(bools)), inclusive)


# ──────── Higher-order functions ─────────────────────────────────────────