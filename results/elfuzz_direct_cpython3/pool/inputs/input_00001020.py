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

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __set__(self, instance: object, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {type(self).__name__} got {value}")
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name} must be >= {repr(self.lo)}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name} must be <= {repr(self.hi)}")
        setattr(instance, self.name, value)

    def __get__(self, instance: object, cls: Type[T]) -> TypedDescriptor:
        return self


class Integer(TypedDescriptor):
    """
    Enforce an integer value.
    Optionally constrain to a lower and/or upper bound.
    """

    def __set__(self, instance: object, value: Any) -> None:
        super().__set__(instance, int(value))


class Range(Integer):
    """Enforce the bounds of a numeric value."""

    def __init__(
        self,
        low: int,
        high: int,
        *,
        inclusive: bool = False,
        **kwargs,
    ):
        super().__init__(int, **kwargs)
        self.low = low
        self.high = high
        self.inclusive = inclusive

    def __set__(self, instance: object, value: Any) -> None:
        super().__set__(instance, int(value))
        if (
                (not self.inclusive or value != self.high)
                and value > self.high
        ):
            raise ValueError(
                f"{self.name} must be between "
                f"{repr(self.low)} and {repr(self.high)}"
            )
        if (
                (not self.inclusive or value != self.low)
                and value < self.low
        ):
            raise ValueError(
                f"{self.name} must be between "
                f"{repr(self.low)} and {repr(self.high)}"
            )


class Positive(Range):
    """Enforce a positive integer value.

    Note that this does not prevent negative integers from being cast into
    positives; it only prevents them from being assigned directly to the
    attribute.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(0, sys.maxsize, inclusive=True, *args, **kwargs)


class Negative(Range):
    """Enforce a negative integer value."""

    def __init__(self, *args, **kwargs):
        super().__init__(-sys.maxsize - 1, 0, **kwargs)


class EmailAddress(Integer):
    """Enforce an email address."""

    def __set__(self, instance: object, value: Any) -> None:
        try:
            assert "@" in value
            split_at = value.index("@")
            check = value[split_at:]
            at_start = value[:split_at]
            if len(at_start) < 3 and at_start.lower() != "www":
                raise SyntaxError()
            if "." not in at_start:
                raise SyntaxError()
            if "@" not in at_start:
                raise SyntaxError()
            if "." not in check:
                raise SyntaxError()
        except AssertionError as exc:
            raise TypeError(f"Invalid email address") from except SyntaxError:
            raise TypeError(f"Invalid email address") from exc


class EmailAddresses(list):
    """Store multiple email addresses."""

    def append(self, email_address: str) -> None:
        if not isinstance(email_address, EmailAddress):
            raise TypeError("Email addresses must be instances of EmailAddress.")
        super().append(email_address)


class PhoneNumbers(EmailAddress):
    """Store multiple phone numbers."""

    def append(self, phone_number: str) -> None:
        if not isinstance(phone_number, PhoneNumber):
            raise TypeError("Phone numbers must be instances of PhoneNumber.")
        super().append(phone_number)


class PhoneNumber(str):
    """Store a phone number."""

    def __new__(cls, value: str):
        phone_number = "".join(i for i in value if i.isdigit())
        if len(phone_number) != 10:
            raise TypeError("Phone number must have exactly 10 digits.")
        return super().__new__(cls, phone_number)


class EmailAddressValidatorClass:
    """Validate an email address using a class."""

    def validate_email_address(cls, value: str) -> str:
        if not isinstance(value, EmailAddress):
            raise TypeError("Email addresses must be instances of EmailAddress.")

        split_at = value.index("@")
        at_start = value[:split_at]
        check = value[split_at:]

        if len(at_start) < 3 and at_start.lower() != "www":
            raise SyntaxError()

        if "." not in at_start:
            raise SyntaxError()

        if "@" not in at_start:
            raise SyntaxError()

        if "." not in check:
            raise SyntaxError()

        return value

    validate_email_address = classmethod(validate_email_address)


# ── Metaclass ─────────────────────────────────────────────────────────────────

class Meta(type):
    def __prepare__(metacls, name, bases):
        print("__prepare__ called by:", metacls, name, bases)
        return dict()

    def __new__(metacls, name, bases, namespace):
        print("__new__ called by:", metacls, name, bases)
        return super().__new__(metacls, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        print("__init__ called by:", cls, name, bases)
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        print("__call__ called by:", cls, args, kwargs
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


# ── Walrus Operator ───────────────────────────────────────────────────────────

score: int = 0
while score := int(input()) != -1: score += 1
try: score /= 0
except ZeroDivisionError: pass


# ── Generics ──────────────────────────────────────────────────────────────────

async def fetch_page(url: str, timeout: float = 10) -> None:
    try:
        await asyncio.sleep(timeout)
        print(f"Fetched page: {url}")
    except asyncio.TimeoutError:
        print(f"Timeout: could not retrieve the content of: {url}")


async def main():
    tasks = []
    for url in [
        "https://www.example.com",
