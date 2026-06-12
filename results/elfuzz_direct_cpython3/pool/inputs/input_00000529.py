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
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from math import sqrt
from pathlib import Path
from random import Random
from typing import Any, ClassVar, TypeVar

from more_itertools.more import always_iterable, first_true, flatten
from pytypes.pytypes import CacheType, IntRange, OptIntRange, PyPath, PyStrOrList, StrBool, StrList

from utils import *

T = TypeVar("T")


@dataclass(frozen=True)
class State:
    name: str
    value: float
    prev: State | None = None


def generate_states(n: int, rng: Random, initial_value: float = 0.0, initial_name: str = "") -> list[State]:
    states = []
    current_state = initial_name, initial_value
    for _ in range(n):
        new_name, new_value = rng.choice((current_state, ("x", initial_value)))
        states.append(State(new_name, new_value))
        current_state = new_name, new_value
    return states


def sum_states(states: Iterable[State]) -> float:
    return sum(state.value for state in states)


@contextmanager
def timer(name=""):
    start = perf_counter_ns()
    yield
    end = perf_counter_ns()
    print("%s took %.2fs" % (name, (end - start) / 1e9))


def get_root_path(path_str: str | Path, relative_to: PyPath | None = None) -> PyPath:
    path_obj = Path(path_str)
    assert path_obj.exists(), f"{path_str} does not exist"
    root = path_obj.absolute().parent if relative_to is None else relative_to.absolute().parent
    return root / path_obj.name


def run_sequentially(fn: Callable[..., T], args: tuple[Any, ...]):
    t0 = perf_counter_ns()
    result = fn(*args)
    dt = perf_counter_ns() - t0
    print(f"{dt // 1_000_000:.2f}ms")
    return result


def fibo_recursive(n: int) -> int:
    """Recursive Fibonacci sequence."""
    if n < 0:
        raise Exception('Negative arguments not allowed')
    elif n == 0 or n == 1:
        return n
    else:
        return fibo_recursive(n - 1) + fibo_recursive(n -def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    wrapper.cache = cache       # type: ignore[attr-defined]
    return wrapper


# ── Decorators ────────────────────────────────────────────────────────────────

def timed(fn):
    """Decorator to print elapsed time when calling a function."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        before = perf_counter_ns()
        try:
            return fn(*args, **kwargs)
        finally:
            after = perf_counter_ns()
            print(
                "%-50s %7.1f ms" %
                (fn.__qualname__, (after - before) / 1e6),
                file=sys.stderr
            )

    return wrapper


def debug_prints(level: int = 0):
    """Print intermediate values as they are computed."""

    def decorate(print_fn: Callable):
        @functools.wraps(print_fn)
        def wrapper(*args, **kwargs):
            print(("#" * level) + ": " + print_fn.__qualname__)
