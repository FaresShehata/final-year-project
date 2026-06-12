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


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn: Callable, *args):
        self.fn = fn
        self.args = args

    def run(self) -> Any:
        while isinstance(self.fn, Thunk):
            self.fn = self.fn.run()
        fn = self.fn
        args = self.args
        del self.fn, self.args
        return fn(*args)


def trampoline(coroutine: Callable[..., Generator]) -> Callable[..., Any]:
    """Trampoline a coroutine."""

    def trampolinized(*args, **kwargs):
        gc = coroutine(*args, **kwargs)
        while True:
            try:
                value = next(gc)
            except StopIteration as exc:
                return exc.value
            else:
                gc = Thunk(value, value)
    return trampolinized


# ── Generators, coroutines, asyncI/O ──────────────────────────────────────────
async def slow_addition(a: int, b: int, delay: int = 2) -> int:
    await asyncio.sleep(delay)
    return a+b


async def slow_task():
    await slow_addition(5, 4)


async def main():
    task = slow_task()

    await asyncio.wait([task])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


# ── Iterables, iterators, and generators ──────────────────────────────────────


def countdown_generator(n=10):
    while n > 0:
        yield n
        n -= 1


def countdown_iterator(n=10):
    while n > 0:
        yield from range(n, 0, -1)


for i in countdown_generator():
    print(i, end=" ")
print()

for i in countdown_iterator():
    print(i, end="")
print()


# ── Higher-order functions, lambdas, filter, map, reduce, zip, enumerate, etc.
# -----------------------------------------------------------------------------

def my_map(func, iterable):
    iterator = iter(iterable)
    return (func(item) for item in iterator)


def my_filter(pred, iterable):
    iterator = iter(iterable)
    return (item for item in iterator if pred(item))


def my_reduce(func, iterrable):
    iterator = iter(iterrable)
    accumulator = next(iterator)
    for item in iterator:
        accumulator = func(accumulator, item)
    return accumulator


def product(nums: Iterable[int]) -> int:
    """Returns the product of an iterable of integers."""
    return functools.reduce(operator.mul, nums, 1)


def sum_of_squares(nums: Iterable[int]) -> int:
    """Sums the squares of an iterable of integers."""
    return functools.reduce(
        lambda x, y: x+y**2,
        nums,
        0,
    )


nums = [i for i in range(10)]
fibonacci_nums = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def square(num: int) -> int:
    return num * num


assert list(my_map(square, fibonacci_nums)) == [0class CachedProperty(TypedDescriptor):
    """A property whose value is computed once per instance and then replaced."""
    
    def __init__(self, func):
        self.func = func
        self.name: str = ""
        
    def __set_name__(self, owner, name):
        self.name = name
        
    def __get__(self, obj, cls):
        if obj is None:
            return self
        val = obj.__dict__[self.name] = self.func(obj)
        return val


# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(type):

    def __prepare__(metacls, name, bases, **kwargs):  # type: ignore[misc]
        return {}

    def __new__(
            metacls,
            name: str,
            bases: tuple[type],
            namespace: dict[str, Any],
            **kwargs: Any,
    ) -> Type[T]:
        if "__module__" in namespace or "__qualname__" in namespace:
            del namespace["__module__"]
            del namespace["__qualname__"]

        if "__slots__" in namespace:
            slots = namespace.pop("__slots__")
            attrs = {}
            for attr in slots:
                attr = attr.strip()
                attrs[attr] = TypedDescriptor(TypeVar(attr))
            namespace.update(attrs)

        print(namespace)
        cls = super().__new__(metacls, name, bases, namespace)
        cls._registry = {}
        for base in reversed(bases):
            reg_cls = registry(base)
            if reg_cls is not None:
                cls._registry |= reg_cls._registry
        reg_cls = registry(cls)
        if reg_cls is not None:
            cls._registry |= reg_cls._registry
        return cls

    def __call__(cls, *args, **kwargs):
        inst = super().__call__(*args, **kwargs)
        key = (inst.__class__.__name__, inst.color)
        cls._registry[key] = inst
        return inst

    def __getitem__(cls, item):
        try:
            return cls._registry[item]
        except KeyError as exc:
<|file_sep|>/seed-06/shape.py
"""
Seed 05 - Decorators & Context Managers
"""


# ── Decorators ────────────────────────────────────────────────────────────────
def debug(func):
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        val = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {val!r}")
        return val

    return wrapper_debug

@debug
def add(x, y):
    return x+y

