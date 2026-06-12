"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""
from typing import Any

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int = 1
    y: float | None = None
    z: bool = False
    a_float: float = 3.456

    @property
    def coords(self) -> tuple[int, float]:
        return self.x, self.y or self.a_float


# ── Async Await ───────────────────────────────────────────────────────────────-

async def fetch_url(url: str) -> str:
    await asyncio.sleep(0.1)
    return url


async def main():
    print("\nASYNC AWAIT 👩‍💻")
    url = "http://www.google.com"
    result = await fetch_url(url)
    print(result)


# ── Protocols ─────────────────────────────────────────────────────────────────

async def process_data(data: bytes) -> str:
    return data.decode("utf-8")


async def main_protocol():
    print("\nPROTOCOLS 🌐")
    raw_bytes = b"\x00\x01\x02\x03ABCDEF\xFF"
    processed = await process_data(raw_bytes)
    print(processed)


# ── Data Classes ───────────────────────────────────────────────────────────────

print("\nDATA CLASSES 🔢")


@dataclass()
class PointDataClass:
    x: int = 1
    y: float | None = None
    z: bool = False
    a_float: float = 3.456

    @property
    def coords(self) -> tuple[int, float]:
        return self.x, self.y or self.a_float


# ── Typing Generics ───────────────────────────────────────────────────────────

class A(list[str]):
    def __init__(self, *args: list[str]) -> None:
        super().__init__(*args)
        self.append("A")

    def count(self) -> int:
        return len(self)

    def append(self, value: str) -> None:
        self.extend([value])


class B(A):
    def __init__(self, *args: list[str]) -> None:
        super().__init__(*args)
        self.append("B")

    def count(self) -> int:
        return len(self)

    def append(self, value: str) -> None:
        self.extend([value])


# ── Exceptions Groups ──────────────────────────────────────────────────────────


@dataclasses.dataclass(slots=True)
class Person:
    """Class with private attribute."""

    _name: str

    def get_name(self) -> str:
        return self._name.upper() if self._name else ""

    def set_name(self, new_name: str) -> None:
        self._name = new_name[:255]

    def __repr__(self) -> str:
        return f"<Person(name={self.get_name()}, ...>"

    def __str__(self) -> str:
        return f"Name: {self.get_name()}"


# ── Slots ─────────────────────────────────────────────────────────────────────

class SlotObject(object):
    __slots__ = ["_x", "_y"]

    def __init__(self, x: int, y: int) -> None:
        self.set(x, y)

    def set(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, SlotObject):
            return NotImplemented
        return not (self == other)

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __repr__(self) -> str:
        return f'<SlotObject(x={self._x}, y={self._y})>'


# ── Structures Pattern Matching ───────────────────────────────────────────────

def match_x_or_y(
    x_or_y: int | float,
    on_x: Callable[[int], None],
    on_y: Callable[[float], None]
) -> None:
    if isinstance(x_or_y, int):
        on_x(x_or_y)
    elif isinstance(x_or_y, float):
        on_y(x_or_y)
    else:
        raise TypeError(f"{x_or_y=} must be an integer or float.")


# ── Walrus Operator ───────────────────────────────────────────────────────────

async def fib(n: int) -> int:
    a, b = 0, 1
    while True:
        if a >= n:
            return a
        yield b
        a, b = b, a + b


async def main():
    print("\n\nWALRUS OPERATOR 🦊")
    async for i in fib(4294967296): ...
    print(i)

