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

class AsyncQueue(Generic[T]):
    def __init__(self, maxsize: int = 0) -> None:
        self._q: asyncio.Queue[T] = asyncio.Queue(maxsize=maxsize)

    async def put(self, item: T) -> None:
        await self._q.put(item)

    async def get(self) -> T:
        return await self._q.get()

    def qsize(self) -> int:
        return self._q.qsize()


async def producer(queue: AsyncQueue[Task], tasks: list[Task], delay: float = 0.0) -> None:
    for task in tasks:
        await asyncio.sleep(delay)
        await queue.put(task)
        task.transition(Status.RUNNING)


async def consumer(
    queue: AsyncQueue[Task],
    results: list[Task],
    n: int,
    fail_ids: frozenset[int] = frozenset(),
) -> None:
    for _ in range(n):
        task = await queue.get()
        await asyncio.sleep(0)          # yield to event loop
        if task.id in fail_ids:
            task.transition(Status.FAILED)
        else:
            task.transition(Status.SUCCESS)
        results.append(task)


async def run_pipeline(tasks: list[Task]) -> list[Task]:
    queue: AsyncQueue[Task] = AsyncQueue(maxsize=10)
    results: list[Task] = []
    fail_ids = frozenset(t.id for t in tasks if t.priority == Priority.LOW)

    await asyncio.gather(
        producer(queue, tasks),
        consumer(queue, results, len(tasks), fail_ids),
    )
    return results


# ── Walrus operator ───────────────────────────────────────────────────────────

def extract_numbers(text: str) -> list[int]:
    pattern = re.compile(r"\d+")
    return [int(m.group()) for line in text.splitlines() if (m := pattern.search(line))]


# ── Structural pattern matching ───────────────────────────────────────────────

def describe_task(task: Task) -> str:
    match task:
        case Task(priority=Priority.URGENT, status=Status.FAILED):
            return "🔥 URGENT FAILURE"
        case Task(priority=Priority.HIGH, status=s) if not s.is_terminal():
            return f"⚡ High-priority still in flight: {s.value}"
        case Task(tags=[*tags]) if "critical" in tags:
            return f"🏷  critical tag present, status={task.status.value}"
        case Task(status=Status.SUCCESS):
            return "✓ done"
        case Task(status=Status.CANCELLED):
            return "✗ cancelled"
        case _:
            return f"? {task.status.value}"


def classify_point(p: Point) -> str:
    match (p.x, p.y):
        case (0.0, 0.0):
            return "origin"
        case (x, 0.0):
            return f"x-axis at {x}"
        case (0.0, y):
            return f"y-axis at {y}"
        case (x, y) if x == y:
            return f"diagonal at {x}"
        case (x, y) if x > 0 and y > 0:
            return "Q1"
        case (x, y) if x < 0 and y > 0:
            return "Q2"
        case (x, y) if x < 0 and y < 0:
            return "Q3"
        case _:
            return "Q4"


# ── ExceptionGroup (Python 3.11+) ─────────────────────────────────────────────

def attempt_exception_group() -> None:
    try:
        raise ExceptionGroup(
            "multiple errors",
            [
                ValueError("bad value"),
                TypeError("wrong type"),
                KeyError("missing key"),
            ],
        )
    except* ValueError as eg:
        print(f"  Caught {len(eg.exceptions)} ValueError(s)")
    except* (TypeError, KeyError) as eg:
        print(f"  Caught {len(eg.exceptions)} TypeError/KeyError(s)")


# ── defaultdict / Counter / deque ────────────────────────────────────────────

def word_analysis(corpus: str) -> dict:
    words = re.findall(r"\w+", corpus.lower())
    freq = Counter(words)
    by_length: defaultdict[int, list[str]] = defaultdict(list)
    seen: deque[str] = deque(maxlen=5)
    for w in words:
        by_length[len(w)].append(w)
        seen.append(w)
    return {
        "total": len(words),
        "unique": len(freq),
        "top5": freq.most_common(5),
        "last5": list(seen),
        "lengths": {k: len(v) for k, v in sorted(by_length.items())},
    }


# ── heapq priority queue ──────────────────────────────────────────────────────

class PQEntry:
    __slots__ = ("priority", "task")

    def __init__(self, task: Task):
        self.priority = -int(task.priority)  # max-heap via negation
        self.task = task

    def __lt__(self, other: PQEntry) -> bool:
        return self.priority < other.priority


def drain_priority_queue(tasks: list[Task]) -> list[Task]:
    heap: list[PQEntry] = []
    for t in tasks:
        heapq.heappush(heap, PQEntry(t))
    return [heapq.heappop(heap).task for _ in range(len(heap))]


# ── overload ──────────────────────────────────────────────────────────────────

@overload
def parse_value(raw: str) -> str: ...
@overload
def parse_value(raw: int) -> int: ...
@overload
def parse_value(raw: float) -> float: ...

def parse_value(raw):
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, int):
        return raw * 2
    if isinstance(raw, float):
        return round(raw, 6)
    raise TypeError(f"Unsupported type: {type(raw)}")


# ── main ──────────────────────────────────────────────────────────────────────

SAMPLE_CORPUS = """
the quick brown fox jumps over the lazy dog
pack my box with five dozen liquor jugs
how vexingly quick daft zebras jump
the five boxing wizards jump quickly
"""

def main() -> None:
    # Tasks
    rng = random.Random(42)
    all_tasks = [
        Task(
            id=i,
            name=f"task-{i:03d}",
            priority=rng.choice(list(Priority)),
            tags=rng.sample(["critical", "optional", "batch", "stream"], k=rng.randint(0, 2)),
        )
        for i in range(1, 16)
    ]

    print("=== Async pipeline ===")
    done = asyncio.run(run_pipeline(all_tasks))
    status_counts = Counter(t.status for t in done)
    for s, n in sorted(status_counts.items(), key=lambda x: x[0].value):
        print(f"  {s.value}: {n}")

    print("\n=== Pattern matching ===")
    for t in done[:6]:
        print(f"  Task({t.id},{t.priority.name}): {describe_task(t)}")

    print("\n=== Point classification ===")
    points = [Point(0, 0), Point(3, 0), Point(0, -2), Point(2, 2), Point(-1, 3)]
    for p in points:
        print(f"  {p} -> {classify_point(p)}")

    print("\n=== Walrus / regex ===")
    nums = extract_numbers("item 12: score 99\nno digits here\nvalue: 42 units: 7")
    print(f"  extracted: {nums}")

    print("\n=== Word analysis ===")
    analysis = word_analysis(SAMPLE_CORPUS)
    for k, v in analysis.items():
        print(f"  {k}: {v}")

    print("\n=== Serialise / deserialise ===")
    raw = json.dumps([t.to_dict() for t in all_tasks[:3]], indent=2)
    restored = [Task.from_dict(d) for d in json.loads(raw)]
    for t in restored:
        print(f"  {t.name} priority={t.priority.name}")

    print("\n=== Priority queue drain ===")
    ordered = drain_priority_queue(all_tasks[:8])
    print("  order:", [f"{t.name}({t.priority.name})" for t in ordered])

    print("\n=== SortedList ===")
    sl: SortedList[int] = SortedList()
    for v in [5, 2, 8, 1, 9, 3]:
        sl.add(v)
    print(f"  sorted: {sl}")
    sl.discard(5)
    print(f"  after discard(5): {sl}")

    print("\n=== Flag enum ===")
    perms = Flag.READ | Flag.WRITE
    print(f"  perms={perms}, has EXECUTE: {Flag.EXECUTE in perms}")
    print(f"  RWX: {Flag.RWX}")

    print("\n=== ExceptionGroup ===")
    attempt_exception_group()

    print("\n=== overload parse_value ===")
    for raw in ["  hello ", 21, 3.14159265]:
        print(f"  {raw!r} -> {parse_value(raw)!r}")


if __name__ == "__main__":
    main()
