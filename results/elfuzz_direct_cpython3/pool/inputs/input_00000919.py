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


def filter_map(some_fn: Callable[[Any], bool | None],
               another_fn: Callable[[Any], T]) -> Callable[[Sequence[T]], Set[T]]:
    """
    Given two functions, `some_fn` and `another_fn`, returns a callable that takes
    an iterable of values and returns the set resulting from applying `some_fn`
    to each value and filtering out those for which `another_fn` returns `None`.
    """

    def filtered_set(iterable: Sequence[T]) -> Set[T]:
        return {another_fn(value) for value in iterable if some_fn(value)}

    return filtered_set


def run_pipeline():
    print(
        "===== PIPELINE =====\n"
        ">>> [2, 4, 6].pipe(add3).map(int_to_church)\n"
        "===> {'8', '12'}\n\n"
        ">>> [2, 4, 6].pipe(map(str)).filter(bool).fold_str(', ', '', '')\n"
        "===> '2, 4, 6'\n"
    )


# ── Partial application using currying ────────────────────────────────────────

def foo1(a: int, b: int, c: int): pass
foo1_ = curry(foo1)


def foo2(a: int, b: int, c: int, d: int): pass
foo2_ = curry(foo2)


def bar():
    print(
        "===== PARTIAL APPLICATION USING CURRYING =====\n"
        ">>> foo1_(b=5)(1, 2)\n"
        "===> ((5 + 1) + 2)\n\n"
        ">>> foo2_(d=9)(a=1, b=2, c=3)\n"
        "===> ((1 + 2 + 3) + 9)\n\n",
    )



# ── Trampoline functions ──────────────────────────────────────────────────────

def factorial(num: int) -> int:
    """Compute the factorial of a number with trampolines.

    Trampolines are used to avoid stack overflow errors when recursion depth
    becomes too large due to the repeated creation of new call frames upon
    recursive calls.
    """
    assert num >= 0

    def impl(n: int, acc: int) -> Callable[[], int]:
        if n == 0:
            return lambda: acc
        return lambda(): impl(n - 1, acc * n)

    return impl(num, 1)()


def memoize(func):
    """Memoizes a function's results so it can be called multiple times without
    recomputing them.

    The decorator works by adding a dictionary attribute `_cache` to the wrapped
    function and storing the results of previous computations under unique keys.
    When the decorated function is called again with the same arguments, it first
    checks the cache to see if the result has already been computed, avoiding the
    computation overhead.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = repr((args, kwargs))
        try:
            return wrapper._cache[key]
        except KeyError:
            res = func(*args, **kwargs)
            wrapper._cache[key] = res
            return res
    wrapper._cache = {}
    return wrapper

if __name__ == '__main__':
    print(sys.version_info.major)
    print(sys.version_info.minor)
    print(sys.version_info.micro)
    print(sys.platform)
    print(sys.path)
    print()
    print(run_pipeline())
    print(church_to_int(ONE))
    print(int_to_church(0))
    print(int_to_church(1))
    print(int_to_church(2))
    print(int_to_church(3))
    print(int_to_church(5))
    print(int_to_church(7))
    print(int_to_church(12))
    print(int_to_church(14))
    print(int_to_church(15))
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
        cache = obj.__dict__
        val = cache.get(self.attrname, _MISSING)
        if val is _MISSING:
            val = self.func(obj)
            cache[self.attrname] = val
        return val


_MISSING = object()

# ── Metaclass ─────────────────────────────────────────────────────────────────

class RegistryMeta(abc.ABCMeta):
    """Metaclass that maintains a registry of all concrete subclasses."""
    
    @classmethod
    def __prepare__(metacls, clsname, bases): # pylint: disable=unused-argument
        return super().__prepare__(clsname, bases)
    
    def __new__(metacls, clsname, bases, clsdict):
        cls = super().__new__(metacls, clsname, bases, clsdict)
        cls._registry.append(cls)
        return cls
    
    @property
    def registry(cls) -> list[type]:
        return cls._registry or []
    
    _registry: ClassVar[list[type]] = []


# ─── Custom Types ─────────────────────────────────────────────────────────────

class SortedList(list):

    def sort(self,
             key=lambda x: x,
             reverse=False,
             /,
             *,
             keyfunc=str.casefold,
             ascending=True,
             case_sensitive=False,
             ):
        # TODO: refactor to support multiple keys
        if not hasattr(keyfunc, "__call__"):
            raise TypeError("'keyfunc' must be callable.")
        
        if case_sensitive:
            self.sort(key=keyfunc, reverse=reverse)
        else:
            # TODO: refactor using 'functools.cmp_to_key' instead of defining custom key function.
            sorted_list = sorted([item for item in self], 
                                 key=(lambda item: (keyfunc(item), item)),
                                 reverse=reverse)
            super().extend(sorted_list)



# ─── Abstract Base Classes ────────────────────────────────────────────────────

class Animal(metaclass=RegistryMeta):
    pass


class Carnivore(Animal):
    pass


class Herbivore(Animal):
    pass


class Omnivore(Carnivore, Herbivore):
    pass


class Cheetah(Omnivore):
    pass


class Lion(Omnivore):
    pass


def get_all_subclasses(class_: type) -> list[type]:
