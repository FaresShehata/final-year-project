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
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import operator
import os
import pickle
import reprlib
import sys
import types
import typing
import unittest.mock
import weakref
import itertools
import functools
import collections

def main():

    # Repr, comparison operators, bools, None, int/float/integral/unpack_sequence_from_iterable
    # subtypes of numbers (complex, float, complex, decimal.Decimal),
    # numeric operations (+,-,*,/, etc.), exponentiation (**), bitwise operators (&, |, ^, <<, >>, ~),
    # identity operators (is, is not), membership operators (in, not in), truth value testing (and, or, not).
    class MyComplex(complex):
        pass
    c = MyComplex(1, 2)
    c.__repr__() == "(1+2j)"
    c.__bool__()
    # True
    c.__int__()
    1j.__eq__(c)
    # True
    c.__pow__(2)
    5.__truediv__(2)
    10.__mod__(3)
    9.__rshift__(2)
    0b11.__xor__(0b10)
    9.__lt__(2)
    # False
    # Python 3.x is true on the first line because we have overridden __eq__ to always return True.
    # Therefore, when you check if 1 == 1, it returns true even though they are different objects.

    # Memoryviews
    memv = memoryview(b"hello")
    print(len(memv))
    print(type(bytes(10)), bytes(10))  # bytearray b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    print(type(memoryview(bytearray(10)).cast("u")), memoryview(bytearray(10)).cast("u"))  # <class 'memoryview'> b'abcdefghij'

    # Array module
    a = array.array("f", [1, 2])
    print(array.array(a.typecode, map(lambda x: x ** 2, a)))
    # [1.0, 4.0]

    # Struct module
    struct.pack("<fff", 1, 2, 3)
    # 16909060.0
    struct.unpack("<iii", b"\    print(lambda x: x ** 2)((lambda y: y * 4)(5))  # 81
    g = lambda x, y: x + y
    f = lambda x: g(x, 1)
    assert f(7) == 8
    d = {"a": [1], "b": ["foo", "bar"]}
    dd = {k: v for k, v in [(x, f(int(y))) if isinstance(y, str) else (y, f(k)) for x, y in d.items()]}

    print(dd)

    def func_with_closing():
        x = 6
        a = "panda"

        def inner_func():
            nonlocal x
            nonlocal a
            x += 1
            a += "!"

        return (x, a)

    print(func_with_closing())  # (7, 'panda!')

    # Higher-order functions
    print(functools.reduce(operator.mul, range(6)))
    print(list(map(operator.add, range(3), range(3))))
    print(
        list(filter(lambda x: x % 2 != 0 and x >= 0, range(-3, 4))),  # [-3, -1]
    )
    print([i**2 for i in range(10)])
    print(list(itertools.takewhile(lambda x: x < 10, [1, 2, 3, 4])))


if __name__ == "__main__":
    main()