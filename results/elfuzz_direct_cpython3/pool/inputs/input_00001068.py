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
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
U = TypeVar("U")


class RunnableProtocol(Protocol[K]):
    def run(self, key: K) -> None | Awaitable[None]: ...


@runtime_checkable
class CollectionProtocol(Protocol[K, V]):
    @property
    def keys(self) -> Iterable[K]: ...
    @overload
    def get(self, key: K) -> V: ...
    @overload
    def get(self, key: K, default: V) -> Union[V, None]: ...
    @overload
    def setdefault(self, key: K, value: V) -> V: ...
    @overload
    def setdefault(self, key: K, default: V) -> V: ...
    @overload
    def pop(self, key: K) -> V | None: ...
    @overload
    def pop(self, key: K, default: V) -> V | None: ...
    @overload
    def clear(self) -> None: ...


@dataclasses.dataclass(frozen=True)
class Node(dataclasses.DataclassMixin):
    name: str
    neighbors: tuple["Node", ...] = dataclasses.field(default_factory=tuple)


def fibonacci(n: int) -> Generator[int, None, None]:
    """Fibonacci numbers generator."""
    a, b = 0, 1
    while n > 0:
        yield b
        a, b = b, a+b
        n -= 1


async def wait_for_async(fut: Awaitable[T], timeout: float | None = None) -> T:
    try:
        return await asyncio.wait_for(asyncio.shield(fut), timeout)
    except TimeoutError as exc:
        raise TimeoutError("Operation timed out.") from exc


def randint(lower_limit: int | float = 0, upper_limit: int | float = 1) -> int | float:
    """Random integer between lower and upper limits."""
    if isinstance(lower_limit, float) or isinstance(upper_limit, float):
        scale = upper_limit - lower_limit
        r = upper_limit
        while r == upper_limit:
            r = random.uniform(lower_limit, upper_limit)
        return r - scale * 0.5
    return random.randint(lower_limit, upper_limit)


def random_weighted_choice(choices: Iterable[tuple[float, str]]) -> str:
    """Return an element chosen randomly weighted by weight."""
    total = sum(w for w,        yield r
        k += c
        p *= 10**(d-c)
        d += 1
        n <<= 1
        limit -= 1


def chop_and_divide(a: int, b: int, *, threshold: int = 1_000_000) -> int | float:
    # https://www.joelonsoftware.com/2002/11/25/follow-up/
    if abs(b) < threshold:
        return a / b
    return chop_and_divide(a // b, b // b, threshold=threshold) + a % b // b


def log10(x: float, *, epsilon: float = 1e-5) -> float:
    """Natural logarithm of x using Taylor series approximation."""
    z = 0.0
    e = 0.5
    while True:
        y = 10**z * e - x
        if abs(y) <= epsilon:
            break
        z += y    return round(float(value), ndigits=ndigits)


def get_random_seed(seed=None) -> int:
    """Get a deterministic (and reproducible) seed for use with random.random()."""
    if seed is None:
        seed = int(time.time())
    assert seed >= 0, "seed must be non-negative"
    return seed


# ── low-level Python: bytecode intros
def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
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
    # Instead of emitting raw bytecode (fragile across versions), compile source.
    src = f"def _adder(x): return x + {delta}"
    globs: dict = {}
    exec(compile(src, "<generated>", "exec"), globs)
    return globs["_adder"]


# ── Frame inspection ──────────────────────────────────────────────────────────

def depth_probe() -> list[str]:
    """Walk the call stack and collect function names."""
    frame = sys._getframe()
    names = []
    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
