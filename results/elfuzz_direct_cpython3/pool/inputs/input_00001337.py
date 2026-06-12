"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import marshal
import weakref

# noinspection PyPep8Naming
if False:
    # noinspection PyUnresolvedReferences
    from typing import Any, Callable, Dict, List, Tuple, TypeVar
T = TypeVar('T')


def f(a: int) -> bool:
    return a > 1


print(f.__code__.co_varnames)
print(f.__code__.co_argcount)

assert isinstance(f.__code__, type(dis.disassemble))

for op in f.__code__.co_code:
    print(hex(op), end=" ")
print()

dis.disassemble(f.__code__)


class A:
    def m(self):
        pass


a = A()
f2 = a.m

print(f2.__closure__)

A.__mro__

print(A.__dict__)


class B:

    def __init__(self):
        self.x = 'x'

    @staticmethod
    def s():
        return 's'


b = B()

print(b.__dict__)
print(B.__dict__)
print(type(b))


def f3(x: A) -> None:
    x.m()


f3(b)


print(isinstance(5, (int, float)))
print(isinstance(5.0, (int, float)))

print(len("hello"))
print(len([1]))
print(len({"hello"}))
print(len({}))
print(len(set()))


def f4() -> str:
    """docstring"""
    return "hello"


help(f4)

print(
    f"python version is {sys.version.split()[0]}\n"
    "Python built-in types:\n\n"
    + f"{[t for t in dir(__builtins__) if not t.startswith('_')]}")

import os

print(os.name)
print(os.environ.get('PATH'))

print('\n'.join(filter(None, [
    ('Python' == 'Python'),
    (True and True),
    (True or False),
    (not True),
    ('abc'.lower()),
])))


def f6(i: int) -> tuple[int]:
    return i * 2 - 1, i ** 2


print(f6(2))

tuple()
list()
set()
dict()


class C(tuple):

    def __new__(cls, x: int) -> object:
        return super().__new__(cls, [x])


c = C(1)

print(c.count(1))

d = c[:]

print(d.count(1))


def g(i: int) -> list[float]:
    l = []
    while len(l) < i:
        l.append(i)
    return l


g(10)

l = []

while len(l) < 10:
    l.append(1)

l = []


def g2(i: int):
    while len(l) < i:
        l.append(i)


g2(10)

del l[:]

l = []

while len(l) < 10:
    l.append(1)


def g3(i: int):
    while len(l) < i:
        l.append(i)


g3(10)

del l[:]


def fib(n: int) -> int:
    if n <= 2:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


fib(10)


def f7(i: int) -> int:
    return i // 2


print(f7.__name__)
print(f7.__annotations__)
print(f7.__defaults__)
print(f7.__kwdefaults__)


def _decorator(func: Callable[[T], T]) -> Callable[[T], T]:
    """
    Decorator function.
    """

    def decorator(*args: List[T], **kwargs: dict[str, T]):
        func(*args, **kwargs)
        return func

    return decorator


@_decorator
def f9(arg: int) -> None:
    print(arg)


f9(1)


def f10(name: str, age: int, weight: float) -> None:
    pass


f10(name='John', age=30, weight=60.5)


def f11(name: str, age: int, *, weight: float) -> None:
    pass


f11(name='John', age=30, weight=60.5)


def f12(name: str = 'John', age: int = 30, weight: float = 60.5) -> None:
    pass


f12(weight=60.5)


def f13(name: str = 'John', age: int = 30, /, weight: float = 60.