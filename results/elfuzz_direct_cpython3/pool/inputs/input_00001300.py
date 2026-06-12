"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import collections.abc as c_abc
import functools
import inspect
import operator
import os
import platform
import random
import reprlib
import re
import sys


# Seed 01 - x is an instance of y
print('Seed 01')
x = [2, None]
if isinstance(x, list):
    print(f'{repr(x)} has type {type(x).__name__}')


# Seed 02 - n is a member of some set A
n = 23
A = (1, 2)
print(n in A)
a = 'hello'
s = 'world'
if n < len(a + s):
    print(repr(a[n:n+len(s)]))
else:
    print(None)

# Seed 03 - f is a callable object with n args
f = lambda *args, **kwargs: kwargs.get('a', None)
print(f(2, 3))

# Seed 04 - t is a tuple whose members are all equal to v
t = ('foo', 'bar') * 5
v = 'foo'
print(t == tuple(v for _ in range(len(t))))

# Seed 05 - x is a subclass of y ??
class BaseClass(object):
    pass


class SubClass(BaseClass):
    pass
print(SubClass.__bases__)


# Seed 06 - x is the same object as y
x = [2, None]
y = x.copy()
print(id(x), id(y))


def foo():
    return 2


print(foo())

print(sys.version_info.minor)


def foo():
    return 2


print(dir(foo))