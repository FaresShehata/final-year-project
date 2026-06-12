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


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c

assert add3(1)(2)(3) == 6

# ── Partial application ──────────────────────────────────────────────────────

def apply_once(fn: Callable, *args: P.args, **kwargs: P.kwargs) -> Callable:
    """Apply one argument to a function with a fixed signature, then return
    that partially applied function.

    >>> from types import MethodType
    >>> class Foo(object):
    ...     @classmethod
    ...     def bar(cls, x, y): pass
    ...
    >>> foo_instance = Foo()
    >>>
    >>> @apply_once(Foo.bar)
    ... def baz(self, x, y):
    ...     print(self, x, y)
    ...
    >>> baz.foo_instance = foo_instance
    >>> baz(5, 7)
    <__main__.Foo object at 0x...> 5 7
    """
    partial_fn = fn(*args, **kwargs)
    return type(fn).__call__(partial_fn)


# ── Trampoline ──────────────────────────────────────────────────────────────

def trampoline(f: Callable[P, T]) -> Callable[P, T]:
    """Trampoline a recursive function using the trampoline algorithm."""

    def trampoline_inner(*args: P.args, **kwargs: P.kwargs) -> T:
        while callable(f(*args, **kwargs)):
            func = f(*args, **kwargs)
            del args[:]
            del kwargs[:]
            if not isinstance(func, tuple):
                args.append(func)
            else:
                args.extend(func[:-1])
                kwargs.update(func[-1])
        return func

    return trampoline_inner


@trampoline
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n-1)


print(factorial(10))


# ── Generators ──────────────────────────────────────────────────────────────

def fib_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


fib_gen = fib_generator()

for _ in range(10):
    print(next(fib_gen))

# ── Coroutines with send() ──────────────────────────────────────────────────

def countdown(name: str = 'world') -> Iterator[int]:
    count = 5
    while count > 0import queue
    print(f'{name}: {countdown}')
    yield count
    count += 1


def countdown2(name='world'):
    count = 5
    while count > 0:
        # Send data to the coroutine.
        yield send(name=name, count=count)
        count -= 1


def send(count: int, name: str) -> Coroutine[Any, Any, int]:
    count -= 1
    if count > 0:
        raise StopIteration(count)
    return count


coroutine = countdown('world')
print(coroutine.send(None))  # prints: world: 5
print(coroutine.send(None))  # prints: world: 4
print(coroutine.send(None))  # prints: world: 3
print(coroutine.send(None))  # prints: world: 2


# ── Exceptions ───────────────────────────────────────────────────────────────

try:
    raise RuntimeError("This is an error you can catch.")
except RuntimeError as exc:
    print(exc)


# ── Context managers ──────────────────────────────────────────────────────────

# context manager that keeps track of how many times it was entered and exited.
class CounterContextManager:
    def __enter__(self) -> CounterContextManager:
        self.count = 0  # keep track of how often this has been used
        return self  # returns itself so we can use `as` to assign to a variable

    def __exit__(self, exc_type, exc_value, traceback):
        print(f'CounterContextManager was called {self.count} times.')

with CounterContextManager() as cm1:
    with CounterContextManager() as cm2:
        print(cm1.count)  # should be 1
        print(cm2.count)  # should be 1
    print(cm1.count)  # should be 2
    print(cm2.count)  # should be 2

# counter = CounterContextManager()
#
# with counter as cnt1:
#     with counter as cnt2:
#         assert cnt1 is cnt2


# ── Unpacking arguments & keyword arguments ───────────────────────────────────


def unpack_args_and_kwargs(*args, **kwargs):
    print(type(args), args)
    print(type(kwargs), kwargs)


unpack_args_and_kwargs(1, 2, 3, key1=1, key2=2, key3=3)

# ── Decorator syntax ──────────────────────────────────────────────────────────


@curry


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(frozen=True)
class Address:
    street_number: str
    street_name: str
    city: str


@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    last_name: str
    age: int
    address: Address
    friends: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Book:
    title: str
    author: str
    isbn: int
    rating: float = 0.0


# ── Slots ─────────────────────────────────────────────────────────────────────

Person.__slots__ = ("name", "last_name")


# ── Structural pattern matching ───────────────────────────────────────────────

def get_status(person: Person) -> str:
    match person:
        case Person(name="John"):
            return "John is here!"
        case Person(name="Jane") as jane:
            return f"{jane.age} years old."
        case _: (friend, *_):
            return f"Hi there, {person.name}. You don't have any friends."


# ── Walrus operator ───────────────────────────────────────────────────────────

def find_person_by_age(
    people: list[Person],
    age: int,
) -> Person | None:
    """Find the first person with the given age or None if not found."""
    for person in people:
        if person.age == age:
            return person

    return None


# ── Generics ──────────────────────────────────────────────────────────────────

async def fetch_data() -> dict[K, V]: ...
async def process_data(data: dict[K, V]) -> None: ...

class Queue(Generic[T]):
    def __init__(self):
        self._queue = []

    def enqueue(self, item: T) -> None:
        self._queue.append(item)

    def dequeue(self) -> T:
        return self._queue.pop(0)


# ── Exception handling ────────────────────────────────────────────────────────

async def handle_exception() -> None:
    try:
        await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nException caught!")
    finally:
        print("Finally block executed.")


# ── Custom exceptions ─────────────────────────────────────────────────────────

class MyError(Exception): pass



# ── Generators ────────────────────────────────────────────────────────────────

def countdown_generator(n: int) -> Iterator[int]:
    yield n
    while n > 0:
        n -= 1
        yield n


def fibo_gen(n: int) -> Generator[float, None, None]:
    """Fibonacci generator.

    >>> list(fibo_gen(7))
    [1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0]
    """
    yield 1.0
