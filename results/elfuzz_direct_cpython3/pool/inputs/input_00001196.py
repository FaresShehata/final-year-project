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

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
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
    async def run(self) -> Result[T]: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True)
class Person:
    first_name: str
    last_name: str
    age: int

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


# ── Slots ─────────────────────────────────────────────────────────────────────

@dataclasses.dataclass(slots=True)
class SlotPerson:
    first_name: str
    last_name: str
    age: int

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


# ── Structural Pattern Matching ───────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Message:
    text: str

    @staticmethod
    def parse(text: str) -> Message:
        return Message(text=text.strip())

    def reply_with(self, new_text: str) -> Message:
        return Message(text=f'You said "{new_text}"')


console = RichConsole()

@console.command()
def hello(name: str):
    message = Message.parse(input('Say something > '))
    message.reply_with(message.text.upper())


# ── Walrus Operator ───────────────────────────────────────────────────────────

print('=' * 80)
print('[blue]Walrus Operator[/]')
print('=' * 80)

console.clear()


# ── Generics ──────────────────────────────────────────────────────────────────

def make_fibonacci_generator(max_value: float) -> Generator[float, None, None]:
    """Generate Fibonacci numbers up to max_value."""
    a, b = 1, 1
    while True:
        result = yield b
        if isinstance(result, float) and abs(b - result) < max_value:
            break
        a, b = b, a + b


async def main_gen():
    """Main generator function."""
    fibonacci_gen = make_fibonacci_generator(0.5)
    next(fibonacci_gen)
    try:
        while True:
            try:
                fib_num = await fibonacci_gen.send(None)
            except StopIteration:
                break
            else:
                console.print(fib_num)
    finally:
        fibonacci_gen.close()


async def main2():
    """Main function."""
    await main_genT = TypeVar('T')
V = TypeVar('V')
K = TypeVar('K', bound=Hashable)


class Status(enum.Enum):
    """Status of an object."""

    OKAY = 'okay'
    WARNING = 'warning'
    ERROR = 'error'


@dataclasses.dataclass(frozen=True)
class Object:
    """An object."""

    status: Status
    name: str
    value: int
    comment: Optional[str] = None


def fibonacci(n: int) -> Iterator[int]:
    yield 1
    if n > 1:
        yield 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
        yield b


async def main() -> None:
    """Main."""
    console = RichConsole()
    console.rule('[bold red]main')

    await asyncio.sleep(0.5)

    console.print(
        '\n\n',
        '[red]'
        '  ● async/await'
        '[/] [yellow]• await...'
        '[/] [purple]• yield...'
        '[/] [cyan]• raise...'
        '[/] [green]• finally...',
        '[/]',
        style='on black on cyan bold',
        end='\n\n'
    )

    async with asyncio.TaskGroup() as tg:
        task_1 = tg.create_task(print('task-1'))
        task_2 = tg.create_task(asyncio.sleep(0.4))
        task_3 = tg.create_task(print('task-3'))

    try:
        await asyncio.gather(task_1, task_2, task_3)
    except RuntimeError:
        pass
    else:
        assert False

    print('\n\n', 'a', 'b', sep='c')

    @overload
    def f(x: int) -> int:
