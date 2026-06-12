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
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)

    def __set_name__(self, owner, name):
        self.attrname = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        # If the method is called with an instance, this will be None because
        # we have set `obj=None` in the constructor.
        cache = obj._cache
        if self.attrname:
            cache = cache.setdefault(self.attrname, {})
        result = cache.get(self)
        if result is None:
            result = cache[self] = self.func(obj)
        return result


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.cnt += 1
        print(wrapper.cnt, ":", end=" ")
        return func(*args, **kwargs)

    wrapper.cnt = 0
    return wrapper


@count_calls
def factorial(n: int) -> int:
    """Calculate n! (factorial of n)."""

    if n < 0 or not isinstance(n, int):
        raise ValueError("n must be a non-negative integer.")
    elif n == 1:
        return 1
    else:
        return n * factorial(n - 1)


# ── Context Managers ──────────────────────────────────────────────────────────

class ContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FileContext(ContextManager):
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()


with FileContext("example.txt", "w") as file:
    file.write("Hello, World!")


# ── Decorators ───────────────────────────────────────────────────────────────

def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("*" * 30)
        result = func(*args, **kwargs)
        print("*" * 30)
        return result

    return wrapper


def my_decorator2(arg1, arg2):
    def inner_decorator(func):
        def wrapper(*args, **kwargs):
            print("=" * 30)
            result = func(*args, **kwargs)
            print("=" * 30)
            return result

        return wrapper

    return inner_decorator


@my_decorator
def foo(x, y):
    print("foo:", x + y)
    return x + y


@my_decorator2("arg1", "arg2")
def bar(x, y):
    print("bar:", x * y)
    return x * y


foo(1, 2)     # foo: 3
foo(4, 8)     # foo: 12
bar(1, 2)     # bar: 2
bar(4, 8)     # bar: 32


def my_decorators_factory(*decorator_funcs):
    def outer(func):
        for decorator_func in reversed(decorators):
            func = decorator_func(func)
        return func

    return outer



# ── Generators ────────────────────────────────────────────────────────────────
genexpr = (yield from range(3))
list(genexpr)      # [0, 1, 2]

iterexpr = iter((yield from range(3K = TypeVar("K")
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
    HIGH   = 9


class Theme(enum.StrEnum):
    LIGHT  = "light"
    DARK   = "dark"


@runtime_checkable
class Message(Protocol[K]):
    message_id: K

    def to_dict(self) -> dict[str, Any]:
        ...

    def from_dict(self, d: dict[str, Any]) -> Self:
        ...


# ── Dataclasses ───────────────────────────────────────────────────────────────
dataclasses.dataclass
dataclasses.field
dataclasses.replace
dataclasses.astuple
dataclasses.asdict


@dataclasses.dataclass(init=False, frozen=True)
class Person():
    first_name: str
    last_name: str

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ── Slots ────────────────────────────────────────────────────────────────────
__slots__ = ["x", "y"]
_=object
class Point(_):
    x: int
    y: int
    z: int = 2


# ── Structural Pattern Matching ──────────────────────────────────────────────

_=Pattern
_=match
_=case
_=_=


# ── Walrus Operator ──────────────────────────────────────────────────────────
a := b
c += d
e -= f


# ── Generics ─────────────────────────────────────────────────────────────────
TypeVar
Generic[T]
re.sub(r"\b[a-z]+\b", lambda m: m.group().upper(), string)


# ── Async ───────────────────────────────────────────────────────────────────-

async def sleep(n: int | float) -> None:
    await asyncio.sleep(n)


async def coroutine_with_yield_from() -> int:
    yield from range(10)
    return sum(range(10))

coroutine_with_yield_from()


# ── Exceptions ───────────────────────────────────────────────────────────────

try:
    ...
except ZeroDivisionError as e:
    print(e.__str__())  # repr()
    print(repr(e))      # str()
    print(e.args)       # tuple(args)
except (TypeError, RuntimeError) as e:
    print(type(e))
else:
    print("no error")


class MyException(Exception):
    def __init__(self, *args: object) -> None:
        pass


ex: MyException = MyException()
print(ex.args        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name}: expected {self.expected_type.__name__}, got {type(value).__name__}"
            )
        if self.lo is not None and value < self.lo:
            raise ValueError(f"{self.name}: {value} below minimum {self.lo}")
        if self.hi is not None and value > self.hi:
            raise ValueError(f"{self.name}: {value} above maximum {self.hi}")
        setattr(obj, self.name, value)


class CachedProperty:
    """Non-data descriptor implementing a lazy cached property."""

    def __init__(self, func):
        self.func = func
