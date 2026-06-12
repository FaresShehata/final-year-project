"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
from typing import Any, ClassVar, Generator, Iterator, Optional, Type, TypeVar

T = TypeVar("T")

# ── Descriptors ──────────────────────────────────────────────────────────────

class TypedDescriptor:
    """Descriptor that enforces a type and optional range constraint."""

    def __init__(self, expected_type: type, lo=None, hi=None):
        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""
    
    def __set_name__(self, owner_class: type, name: str) -> None:
        print(f"{owner_class.__name__}.{name} descriptor")
        self.name = name
    
    def __get__(self, instance: T, owner_class: type | None = None) -> Any:
        return getattr(instance, self.name)
    
    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type): raise TypeError(
            f"Expected {self.expected_type}, got {type(value)} instead"
        )
        if self.lo is not None and value < self.lo: raise TypeError(
            f"Expected a number >= {self.lo}, got {value} instead"
        )
        if self.hi is not None and value > self.hi: raise TypeError(
            f"Expected a number <= {self.hi}, got {value} instead"
        )
        
        setattr(instance, self.name, value)


class Integer(TypedDescriptor):
    """Integer descriptor that enforces range constraints."""
    def __init__(self, lo=None, hi=None):
        super().__init__(int, lo, hi)
    

class Float(TypedDescriptor):
    """Float descriptor that enforces range constraints."""
    def __init__(self, lo=None, hi=None):
        super().__init__(float, lo, hi)
    
    
class String(TypedDescriptor):
    """String descriptor that enforces lower and upper bounds on the length of strings."""
    def __init__(self, lo: int | None = None, hi: int | None = None):
        super().__init__(str, lo, hi)
        
        
class Bool(TypedDescriptor):
    """Boolean descriptor that enforces an exact boolean value."""
    def __init__(self):
        super().__init__(bool)
        

class Choice(TypedDescriptor):
    """Choice descriptor that enforces an exact choice from a list of choices."""
    def __init__(self, choices: set[Any], allow_none: bool = False):
        super().__init__(None, None, None)
        self.choices: set[Any] = choices.copy() if allow_none else choices.copy().difference({None})
        
    
class Enum(TypedDescriptor):
    """Enum descriptor that enforces an exact enumeration value."""
    def __init__(self, enum: Type[enum.Enum], allow_none: bool = False):
        super().__init__(None, None, None)
        self.enum: Type[enum.Enum]    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
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

    # comparison key ignores status and history
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Task): raise TypeError()
        return (self.priority.value, self.id) < (other.priority.value, other.id)

    @property
    def history(self) -> tuple[Status, ...]: return tuple(self._history)
    
    @history.setter
    def history(self, value: Iterable[Status]): self._history.clear(), self._history.extend(value)

    @overload
    def merge(self, task: Task) -> None: ...
    @overload
    def merge(self, tasks: list[Task]) -> None: ...
    
    def merge(self, tasks: Union[Task, list[Task]]) -> None:
        if isinstance(tasks, Task):
            tasks = [tasks]
            
        if len(tasks) == 0:
            raise ValueError("Cannot merge empty tasks.")
        
        merged_priority = max(task.priority for task in tasks)
        merged_tags = sorted(set.union(*(task.tags for task in tasks)))
        merged_metadata = {}
        for task in tasks:
            merged_metadata.update(task.metadata)
            merged_history = [*task.history]
            merged_history.reverse()
            self._history = merged_history
        
        self.priority = merged_priority
        self.tags = merged_tags
        self.metadata = merged_metadata


# ── Collections ───────────────────────────────────────────────────────────────-

@dataclasses.dataclass
class Statistics(Generic[K, V]):
    total: int = 0
    min_value: Optional[V] = None
    max_value: Optional[V] = None
    mean: Optional[float] = None
    median: Optional[V] = None
    values: List[V] = dataclasses.field(default_factory=list, init=False, hash=False, eq=False, compare=False)
