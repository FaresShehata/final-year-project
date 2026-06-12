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

TRUE  = lambda t: lambda f: t   # λt.λf.t
FALSE = lambda t: lambda f: f    # λt.λf.f

AND    = lambda a: lambda b: a(b)(a)  # λa.λb.a(b)(a)
OR     = lambda a: lambda b: a(a)(b)  # λa.λb.a(a)(b)

NOT    = FALSE(AND(TRUE(FALSE)))  # λx.x(x)(λy.y)

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