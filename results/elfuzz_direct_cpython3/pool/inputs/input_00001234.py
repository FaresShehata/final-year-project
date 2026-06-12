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
C = TypeVar("C", bound="BaseClass")
D = TypeVar("D")


class BaseClass(metaclass=abc.ABCMeta):
    """Dummy base class."""

    __slots__ = ()

    def __call__(self: C) -> D:
        raise NotImplementedError()

    def __new__(
        mcs: type[type[C]],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> type[D]:
        if "__abstractmethods__" not in namespace and "__abstractmethods__" in getattr(mcs, "__dict__"):
            abstracts = mcs.__dict__["__abstractmethods__"]
            for attr_name in abstracts:
                namespace.setdefault(attr_name, lambda _: NotImplemented)
        return super().__new__(mcs, name, bases, namespace)


class Foo(BaseClass): ...
Foo()


class Bar(BaseClass):
    @property
    def prop(self) -> str: ...
Bar.prop


def baz() -> None: ...
baz()


# ── Decorators ────────────────────────────────────────────────────────────────

class CountCalls: 
    """Decorator that keeps track of the number of times a function is called."""
    
    def __init__(self, func): 
        self.func = func 
        self.num_calls = 0 
        
    def __call__(self, *args, **kwargs): 
        self.num_calls += 1 
        print(f"Call {self.num_calls} of {self.func.__name__!r}") 
        return self.func(*args, **kwargs) 
    
    @property 
    def count(self): 
        return self.num_calls 

@CountCalls
def say_whee(): 
    print("Whee!") 
say_whee()


def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("I am about to call the real deal")
        result = func(*args, **kwargs)
        print("I have just called the real deal")
        return result
    
    return wrapper


@my_decorator
def add(x,y):
    return x+y


add(8,9)


# ── Context Managers ───────────────────────────────────────────────────────────

class MyContextManager:

    def __enter__(self):
        print("Entering...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting...")

with My    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
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

    def __post_init__(self):
        assert isinstance(self.priority, Priority), f"{type(self.priority)} is not a `Priority` instance."
        assert len(self.tags) == 0 or all(isinstance(tag, str) for tag in self.tags)

    @property
    def is_done(self) -> bool:
        return self.status in {Status.SUCCESS, Status.FAILED}

    @property
    def is_urgent(self) -> bool:
        return self.priority.value >= Priority.URGENT.value

    def __lt__(self, other: Task) -> bool:
        return self.priority > other.priority

    def __repr__(self) -> str:
        fields_str = ", ".join(
            field.name + "=" + repr(getattr(self, field.name)) for field in dataclasses.fields(self)
        )
        return f"<{self.__class__.__qualname__}: ({fields_str})>"

    def __str__(self):
        return f"[{self.id}] {self.name}"

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (
            self.id == other.id
            and self.name == other.name
            and self.priority == other.priority
            and self.status == other.status
            and self.tags == other.tags
            and self.metadata == other.metadata
        )

    def __hash__(self):
        return hash((self.id, self.name))

# ── Generators ─────────────────────────────────────────────────────────────────

def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1

for i in infinite_sequence():
    print(i)


async def counter(max_value):
    value = 0
    while value < max_value:
        await asyncio.sleep(1)
        yield value
        value += 1

async def main():
    async for value in counter(3):
        print(value)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

# ─── Tokenizer ────────────────────────────────────────────────────────────────

from tokenize import NUMBER as TOKEN_NUMBER
from tokenize import STRING as TOKEN_STRING
from tokenize import NAME as TOKEN_NAME
from tokenize import LPAR as TOKEN_LPAR
from tokenize import RPAR as TOKEN_RPAR
<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>from tokenize import INDENT as TOKEN_INDENT
from tokenize import DEDENT as TOKEN_DEDENT
from tokenize import OP as TOKEN_OPERATOR
from tokenize import ENDMARKER as TOKEN_ENDMARKER
from tokenize import ERROR as TOKEN_ERROR
from tokenize import EOF as TOKEN_EOF
from tokenize import COMMENT as TOKEN_COMMENT
from tokenize import NL as TOKEN_NEWLINE
from tokenize import INDENT as TOKEN_INDENT
from tokenize import DEDENT as TOKEN_DEDENT
