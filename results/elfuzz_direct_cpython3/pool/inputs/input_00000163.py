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

def is_zero(n) -> bool:
    return n(IF(FALSE))(TRUE)


# ── Higher-order functions, currying, partial application and trampolining ────
#
# A decorator that ensures the function doesn't exceed the recursion limit.
#

def safe_recursion_limit(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        original = sys.getrecursionlimit()
        try:
            sys.setrecursionlimit(max(original * 2, func.count + 1))
            return func(*args, **kwargs)
        finally:
            sys.setrecursionlimit(original)

    wrapper.count = 0
    return wrapper


# ── Partial application of lambdas ────────────────────────────────────────────

multiply_by_two = lambda x: x * 2
add_one = lambda x: x + 1

double_and_add_one = multiply_by_two(add_one)
double_and_add_one_lambda = lambda x: multiply_by_two(x) + 1
square_add_three = lambda x: (x**2) + 3

assert double_and_add_one(7) == square_add_three(4), "The two expressions are not equivalent"
assert double_and_add_one_lambda(7) == double_and_add_one(7), "Lambdas don't preserve partial applications"

# ── Trampoline implementation ────────────────────────────────────────────────

def trampoline(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    while True:
        result = func(*args, **kwargs)
        if hasattr(result, "__call__"):
            args = result.args  # type: ignore[attr-defined]
            kwargs = result.kwargs  # type: ignore[attr-defined]
        else:
            return result


def factorial(n: int) -> int:
    return trampoline(
        lambda n, acc=1: (
            (lambda acc: (acc := acc * n)(n-1)) if n > 0 else acc
        ),
        n
    )

assert factorial(6) == 720, "factorial failed on test case"


# ── Iterators, generators and coroutines ─────────────────────────────────────

def fibs() -> Iterator[int]:
    a = 0
    b = class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        return cls(
            id=data["id"],
            name=data["name"],
            priority=Priority[data.get("priority", "NORMAL")],
            status=Status(data.get("status", "pending")),
            tags=data.get("tags", []),
        )


assert isinstance(Task(1, "t"), Serialisable), "Task should satisfy Serialisable"


# ── Generic container ─────────────────────────────────────────────────────────

class SortedList(Generic[T]):
    """Keeps elements sorted using bisect."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def add(self, item: T) -> None:
        bisect.insort(self._data, item)  # type: ignore[arg-type]

    def discard(self, item: T) -> None:
        idx = bisect.bisect_left(self._data, item)  # type: ignore[arg-type]
        if idx < len(self._data) and self._data[idx] == item:
            self._data.pop(idx)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"SortedList({self._data!r})"


# ── Async machinery ───────────────────────────────────────────────────────────

