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
        return super().__new__(C, [x])


c = C(1)
print(c)
print(C([1]))

array.array('i', [1, 2])

ctypes