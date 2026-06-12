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

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> Task: ...


def task_runner(task: Task) -> Task:
    print(f"Running task {task.id}:", end=" ")
    for t in range(random.randint(3, 8)):
        print(".", end="", flush=True)
        await asyncio.sleep(random.random() / 10)
    if random.choice([True, False]):
        raise RuntimeError("Oops!")
    task.transition(Status.SUCCESS)
    print("done")
    return task


async def main() -> None:
    tasks: list[Task] = [
        Task(id=i, name=f"Task-{i}") for i in range(7)
    ]
    pending_tasks: list[Tuple[int, Task]] = []

    while True:
        num_pending = len(pending_tasks)
        for idx, task in reversed(sorted(tasks)):
            if task.status.is_terminal():
                continue
            if task.priority >= priority and task not in pending_tasks:
                pending_tasks.append((idx, task))
                break
        else:
            
            if len(pending_tasks) < num_pending:
                
                _, task = pending_tasks.pop(random.randrange(len(pending_tasks)))
                task.transition(Status.RUNNING)
                await asyncio.create_task(task_runner(task))


# ── Iterators & Generators ───────────────────────────────────────────────────-

def fibonacci(n: int) -> Generator[int, None, None]:
    a, b = 0, 1

    yield 0

    for _ in range(n-1):
        a, b = b, a+b
        yield a


def fib_generator(n: int) -> Iterator[int]:
    a, b = 0, 1

    yield 0
    for _ in range(n-1):
        a, b = b, a+b
        yield a


def count_from_one(n: int) -> Iterator[int]:
    for i in range(n+1):
        yield i


def count_from_two() -> Iterator[int]:
    i = 2
    while True:
        yield i
        i += 2


def take(limit: int, iter: Iterable[T]) -> list[T]:
    result: list[T] = []
    for item in iter:
        result.append(item)
        if len(result) == limit:
            break
    return result


def skip(limit: int, iter: Iterable[T]) -> list[T]:
    result: list[T] = []
    next(iter)
    for item in iter:
        result.append(item)
        if len(result) == limit:
            break
    return result


# ── Exceptions ────────────────────────────────────────────────────────────────

async def throw_err(*exceptions: BaseException):
    await asyncio.sleep(random.random())
    await asyncio.shield(asyncio.throw(*exceptions))


async def catch_err(coroutine: Coroutine):
    try:
        await coroutine
    except Exception as exc:
        print(exc)


# ── Timeouts ──────────────────────────────────────────────────────────────────

async def timeout_after(seconds: float, coroutine: Awaitable[T]) -> T:
    delay = asyncio.TimeoutError()
    future = asyncio.ensure_future(coroutine)
    done, pending = yield from asyncio.wait(
        [delay, future],
        timeout=seconds,
        return_when=asyncio.ALL_COMPLETED            current_label = ""
    return counts


def get_instructions(fn) -> list[tuple[int, str]]:
    instructions: list[tuple[int, str]] = []
    for i, op in enumerate(dis.findlinestarts(fn)):
        label = dis.opname[op]
        if label.startswith('EXTENDED_ARG'):
            continue
        elif label == 'SETUP_LOOP':
            instructions.append((i, label))
        elif label.endswith('_LOOP'):
            instructions.extend([(i, label)])
    return instructions


def get_instruction_sources(fn) -> dict[str, list[str]]:
    sources: dict[str, list[str]] = {}
    for lineno, instruction in get_instructions(fn):
        source = fn.co_lnotab[lineno * 2 : lineno * 2 + 2]
        if source:
            offset = ord(source[-1])
            source = fn.co_code[lineno * 2 :]
            instruction += f"(offset {hex(offset)}) "
        instruction += f"(source line {dis.showlinerange(fn)}})"
        if instruction not in sources.values():
            sources[f"{lineno}. {instruction}"] = []
        sources[f"{lineno}. {instruction}"].append(instruction)
    return sources


# ── disassembling functions ───────────────────────────────────────────────────

def get_function_argspec(fn) -> inspect.FullArgSpec:
    return inspect.getfullargspec(fn)


def get_function_annotations(fn) -> dict[str, type]:
    return fn.__annotations__


def get_function_defaults(fn) -> tuple[Any]:
    return fn.__defaults__


# ── CodeObjects ───────────────────────────────────────────────────────────────

def get_func_code(fn) -> types.CodeType:
    return fn.__code__


def get_func_co_varnames(fn) -> tuple[str]:
    return fn.__code__.co_varnames


def get_func_co_argcount(fn) -> int:
    return fn.__code__.co_argcount


def get_func_co_nlocals(fn) -> int:
   

def get_docstring(fn) -> str | None:
    return fn.__doc__ or ""


def compile_fn(fn, filename="<fn>", flags=None) -> types.CodeType:
    assert isinstance(fn, types.FunctionType)
    return compile(get_source(fn), filename, "exec", flags or "exec")


def build_frame(f_globals: dict[str, Any], f_locals: dict[str, Any]) -> types.FrameType:
    return types.FrameType(
        globals=f_globals,
        locals=f_locals,
        f_back=sys._getframe(),
        f_trace=None,
        f_code=get_code_obj(type(f_globals)),
    )


def get_source_lines(obj: object) -> tuple[list[str], int]:
    nlines = obj.co_firstlineno - 1
    lines = inspect.getsourcelines(obj)[0][nlines:]
    return lines, nlines


def get_bytecode(obj: object) -> bytes:
    return marshal.dumps(obj.co_code)


# ── ctors & destructors ───────────────────────────────────────────────────────

def make_nonzero(x: object, y: object) -> bool:
    if x != y:
        return True
    else:
        raise ValueError("zero")


