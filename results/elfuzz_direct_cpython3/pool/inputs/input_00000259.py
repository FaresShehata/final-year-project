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

VARS = [
    ZERO,
    ONE,
    TWO,
    THREE,
    FALSE,
    TRUE,
    AND,
    OR,
    NOT,
    ADD,
    MUL,
    SUCC,
]


def show_eval(expr: Any, vars: list[Any]) -> any:
    """
    >>> show_eval(TRUE(), VARS)
    True

    >>> show_eval(IF(TRUE()), VARS)
    3
    """

    for v in vars:
        if expr == v:
            return v
    else:
        return IF(show_eval(expr[0], vars))(show_eval(expr[1], vars))(
            show_eval(expr[2], vars)
        )


# ── Higher-order functions, map/filter/reduce/reduce-left/accumulate/map-acc/… ──

F = Callable[[Any], Any]


def map_acc(f: F, iterable: Iterable[A], initial: B = None) -> list[B]:
    """
    >>> map_acc(lambda a: a * 2, [0, 1, 2])
    [0, 2, 4]

    >>> map_acc(lambda a: a * 2, [0, 1, 2], 1)
    [1, 2, 4]
    """
    result: list[B] = []
    total = initial or 0
    for i, e in enumerate(iterable):
        result.append(total := total + f(e))
    return result


def filter_acc(predicate: F, iterable: Iterable[A], default: A | None = None) -> list[A]:
    """
    >>> filter_acc(lambda a: a > 10, [0, 1, 2, 3, 4])
    [11, 12, 13, 14]

    >>> filter_acc(lambda a: a > 10, [0, 1, 2, 3, 4], 100)
    [100, 101, 102, 103, 104]
    """
    result: list[A] = []
    for e in iterable:
        if predicate(e):
            result.append(e)
        else:
            result.append(default)
    return result


def reduce_acc(
    func: Callable[[B, A], B], iterable: Iterable[A], initval: B = None
) -> B:
    """
    >>> reduce_acc(operator.add,
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

