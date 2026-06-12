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
    def coords(self):
        return (self.x, self.y or self.a_float)


def sum_coords(point: PointDataClass) -> int:
    return point.x + sum([1, 2])


def my_func(point: Point, *args, **kwargs) -> None:
    print(f"Point: {point}")
    print(args)
    print(kwargs)

    if isinstance(point, PointDataClass):
        print("isinstance(PointDataClass)")


my_func(Point(), 1, 2, 3, 4, name="foo", age=20)
print(sum_coords(Point()))
print(sum_coords(PointDataClass()))


# ── Slots & Structural Pattern Matching ───────────────────────────────────────

print("\nSlots & Structural Pattern Matching ⚡")

data = {
    'name': 'John',
    'age': 30,
    'city': 'New York'
}

for key in data.keys():
    print(key)
print()

for value in data.values():
    print(value)
print()


# ── Walrus Operator ────────────────────────────────────────────────────────────

print("\nWalrus Operator 🦄")

for (key := input('Name: '), val := input('Age: ')) in (
    ('john', 20),
    ('doe', 30),

):

    print(f"{key} is {val} years old.")


# ── Generics ───────────────────────────────────────────────────────────────────

print("\nGenerics 📊")


def add_numbers(a, b):
    return a + b


print(add_numbers(1, 2))


def add_strings(a: str, b: str):
    return f'{a}-{b}'


print(add_strings("Hello", "World"))


def add_a_and_b(*args):
    return args[0] + args[1]


print(add_a_and_b(1, 2))

# ── Exception Groups ────────────────────────────────────────────────────────────


def divide_by_zero():
    raise ZeroDivisionError("Cannot divide by zero!")


try:
    divide_by_zero()
except ZeroDivisionError as e:
    pass
else:
    return True
finally:
    return False


try:
    divide_by_zero() or True
except ZeroDivisionError as e:
    pass
else:
    return True
finally:
    return False


try:
    divide_by_zero() and False
except Zero    print("\nList comprehension:")
    xs = [i+1 for i in range(4)]
