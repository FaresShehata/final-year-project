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

def churchify(func: Callable[[int], int]) -> Callable[[Callable[[int], int]], Callable[[Callable[[int], int]], Callable[[int], int]]]:
    """
    Church's encoding of abstractions.

    >>> churchify(int).__call__(int). __call__(10)
    10
    """

    return lambda f: lambda x: func(f(x))

churchify = functools.partial(churchify)

# ── Currying & Partial Application ───────────────────────────────────────────-

def curry(func: Callable[..., B], *args: A, **kwargs: Any) -> Callable[..., B]: ... 

curry = functools.partial(lambda func, *args, **kwargs: lambda func, *more_args, /, **more_kwargs: func(*(args or more_args), **{**kwargs or more_kwargs}))
partial = curry

add_curried = curry(operator.add, 1, 2)
add_partial = partial(operator.add, 1, 2)

# ── Recursion via Iterators and Generators ───────────────────────────────────-

def countdown(n: int) -> Iterator[int]: ...
def countdown_iter(n: int) -> Iterator[int]: ...

countdown_generator = countdown_iter
countdown_iterator = countdown_iter

# ── Trampoline-based Y-combinator implementation ─────────────────────────────-

TRAMPOLINE_DEPTH_LIMIT = 10_000

def trampoline(fn: Callable[..., Any]) -> Callable[..., Any]: ...
trampoline = functools.reduce(operator.methodcaller('bind'), reversed([lambda fn: lambda *args, **kwargs: fn(*args, **kwargs)]*TRAMPOLINE_DEPTH_LIMIT), lambda fn: lambda *args, **kwargs: fn(*args, **kwargs))


# ── Higher-Order Functions and First-Class Functions ───────────────────────────

def show_result(fn: Callable[..., Any], args: tuple[Any, ...]) -> None:
    try:
        result = fn(*args)
        print(f"{fn.__name__}({', '.join(map(repr, args))}) => {result}")
    except Exception as e:
        print(f"{fn.__name__}({', '.join(map(repr, args))}): {e}")


show_result(SUCC, (ONE,))
show_result(SUCCESSFUL_OPERATION, ())
show_result(IF, (True,))
show_result(AND, (ZERO, ONE))
show_result(OR,    CANCELLED = "cancelled"

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

    def get_distance_to_origin(self) -> float:
        return (self.x**2 + self.y**2)**0.5
    

PointList = list[Point]


@dataclasses.dataclass(frozen=True)
class LineSegment:
    point_a: Point
    point_b: Point

    @property
    def length(self) -> float:
        dx = self.point_a.x - self.point_b.x
        dy = self.point_a.y - self.point_b.y
        return (dx**2 + dy**2)**0.5
    
    def intersects(self, other: LineSegment) -> bool:
        return False


def create_point_list(n: int) -> PointList:
    return [Point(x=random.random(), y=random.random())
            for _ in range(n)]

# ── Slots ─────────────────────────────────────────────────────────────────────

class Person:
    name: str
    age: int
    gender: str

    __slots__: ClassVar[list[str]] = ["age", "gender"]


p1: Person = Person(name="John Doe", age=30, gender="male")
print(p1.__dict__)       # {'name': 'John Doe'}
print(p1.age)            # 30
del p1.name              # AttributeError: can't delete attribute '__weakref__'
with open("person.json", mode="w+") as f: json.dump(dataclasses.asdict(p1), f)


# ── Structural Pattern Matching ───────────────────────────────────────────────

@overload
def is_person(obj: object) -> bool: ...
@overload
def is_person(obj: Person) -> bool: ...
def is_person(obj): return isinstance(obj, Person)

person = {"name": "Alice", "age": 28}
for key, value in person.items(): print(key, value)
match person:
    case {"name": n, "age": a} if is_person(person):
        print(f"Name: {n}, Age: {a}")
    case {"name": _, "age": _}:
        print("Key-value pairs with name and age found")
    case {}:
        print("No key-value pairs found")
    case _: raise ValueError("Invalid person dictionary")


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def fetch(url: str) -> bytes:
    await asyncio.sleep(random.randint(0, 4))
    return b"data"


urls: list[str] = [
    "https://example.com",
    "https://google.com",
    "https://yahoo.com",
]

tasks = []
for url in urls:
    task = asyncio.create_task(fetch(url))
    tasks.append(task)
    match await task: 
        case bytes():
            print(f"Fetched data from {url}")

# ── Typing Generics ───────────────────────────────────────────────────────────

class Stack(Generic[T]):
