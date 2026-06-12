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
    TYPE_CHECKING, AnyStr, BinaryIO, Callable, ClassVar, Dict, Generic, Hashable, Iterable, Iterator, List, Mapping,
    Match, MutableMapping, Optional, Pattern, Set, Sequence, Tuple, TypeVar, Union, cast, overload)
from weakref import WeakKeyDictionary


if TYPE_CHECKING:
    from types import TracebackType

    from rich.console import Console as RichConsole
else:
    from unittest.mock import MagicMock as RichConsole  # type: ignore[assignment]


T = TypeVar('T')
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
