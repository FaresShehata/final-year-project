"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Sequence, Set
from dataclasses import dataclass, field
from functools import partial
from inspect import isasyncgenfunction, iscoroutinefunction, signature
from itertools import chain, cycle, dropwhile, groupby, tee
from types import GeneratorType, UnionType
from types import ModuleType as _ModuleType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    overload,
    runtime_checkable,
)


T = TypeVar("T")
U = TypeVar("U")


# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(str, enum.Enum):
    PENDING         = "pending"
    RUNNING         = "running"
    COMPLETED       = "completed"
    FAILED          = "failed"
    PRESENT         = "present"
    NON_EXECUTABLE  = "non-executable"


class ResultStatus(enum.Enum):
    SUCCESS     = enum.auto()
    FAILURE     = enum.auto()


@runtime_checkable
class AsyncIterable(Protocol[T]):
    def __aiter__(self) -> AsyncIterator[T]:
        ...


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclass(order=True)
class Node:
    id: int
    name: str
    depth: int
    priority: float
    status: Status = Status.PRESENT
    children: list[Node] = field(default_factory=list)

    def insert(self, node: Node) -> None:
        if node.id == self.id:
            raise ValueError(f'"{node}" already exists')
        parent_id = node.parent_id
        for child in self.children:
            if child.id == parent_id:
                child.insert(node)
                return
        self.children.append(node)

    @property
    def parent_id(self) -> int | None:
        try:
            return self.get_parent().id
        except AttributeError:
            return None

    @property
    def get_parent(self) -> Node:
        for child in reversed(self.children):
            if child.depth == self.depth - 1:
                return child
        raise IndexError()

    @property
    def is_root(self) -> bool:
        return self.depth == 0

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def level(self) -> int:
        return self.depth + (len(self.children) * 100)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} "
        + (" ".join([f'{k}={v}' for k, v in vars(self).items()]))
        + ">"


def create_tree(root: int | Node):
    nodes = [root]
    for i in range(len(nodes)):
        if isinstance(nodes[i], int):
            nodes.extend(Node(id=i, name=f"{nodes[i]}-{j}") for j in range(3))
            nodes[i].insert(nodes[-3])
            nodes[i].insert(nodes[-2])
            nodes[i].insert(nodes[-1])


if __name__ == "__main__":
    a = Node(id=0, name="A", depth=0)
   