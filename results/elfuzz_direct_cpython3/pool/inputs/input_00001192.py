"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated, Callable, ClassVar, Concatenate, Coroutine, DefaultDict, Dict, Generator, Generic, Literal,
    NamedTuple, NonEmptySequence, ParamSpec, Protocol, Sequence, Set, Tuple, TypedDict, Union, cast)
from types import TracebackType
from typing_extensions import Self, TypeAlias, TypeGuard, Unpack, get_args, get_origin, get_type_hints
from collections.abc import AsyncGenerator, Awaitable


def _test_str():
    print('type: str')
    s1 = 'Hello world.'
    print(s1)
    s2 = """Hello \
        world."""
    print(s2)

    # f-strings
    name = 'Bob'
    age = 40
    print(f'{name} is {age}')

    # format()
    print('{} is {}'.format(name, age))

    # raise exception
    try:
        raise ValueError()
    except ValueError:
        pass

    # assert
    a: int = 1
    assert isinstance(a, int) and a > 0

    # type hint
    def foo(x: int | float):
        return x + 1

    # inspect
    print(ast.dump(foo))
    del foo
    print(reveal_type(foo))


def _test_int():
    print('type: int')
    i1 = 2 ** 31 - 1
    print(i1)
    i2 = -i1
    print(i2)

    # bit shift left
    bsl = 1 << 7
    print(bsl)

    # bit shift right
    bsr = 1 >> 1
    print(bsr)

    # bit mask
    mask = 0b1000_0000
    print(mask & i1)

    # bit check
    if i2 & mask != 0:
        print(True)


def _test_float():
    print('type: float')
    f1 = 2.98e+308
    print(f1)
    f2 = -f1
    print(f2)

    # inf
    print(float('inf'))
    print(-float('inf'))

    # nan
    print(float('nan'))


def _test_bool():
    print('type: bool')
    b1 = True
    b2 = False
    print(b1 or b2)
    print(not b1)


def _test_bytes():
    print('type: bytes')
    byte_string = '\x08\x0c'.encode()
    print(byte_string)

    # unpack bytes to ints
    for byte in byte_string:
        print(byte)


def _test_bytearray():
    print('type: bytearray')
    byte_array = bytearray('\x08\x0c', encoding='utf-8')
    print(byte_array)
    for i, value in enumerate(byte_array):
        print('{:<3d}: {:<3o}'.format(i, value))


def _test_complex():
    print('type: complex')
    c1 = 4j
    c2 = 2 * 1j
    print(c1 + c2)
    print(1j + 1j)
    print(1j * 1j)

    # polar representation
    r, phi = cmath.polar(1 + 2j)
    print(r, phi)

    # exponential form
    re, im = cmath.exp(1 + 2j)
    print(re, im)


def _test_set():
    print('type: set')
    s1 = {'a', 'b'}
    s2 = set(('c', 'd'))
    s3 = {s1, s2}
    print(s3)

    # mutable set
    s1.add('e')

    # copy
    s2 = s1.copy()

    # difference
    s4 = s1.difference(s2)
    print(s4)

    # intersection
    s4 = s1.intersection(s2)
    print(s4)

    # symmetric_difference
    s4 = s1.symmetric_difference(s2)
    print(s4)

    # union
    s4 = s1.union(s2)
    print(s4)

    # update
    s1.update({'z'})
    print(s1)


def _test_frozenset():
    print('type: frozenset')
    s1 = frozenset(['a', 'b'])
    s2 = frozenset(('c', 'd'))
    s3 = s1 | s2
    print(s3)


def _test_tuple():
    print('type: tuple')
    t1 = ('a',)
    t2 = ('b',)
    t3 = t1 + t2
    print(t3)

    # immutable tuple
    t1[0] = 'A'

    # count
    print(t3.count('b'))

    # find first position of element
    print(t3.index('b'))



def _test_dict():
    print('type: dict')
    d1 = {'key': 'value'}
    d2 = dict(key='value')
    d3 = dict([('key', 'value')])
    d4 = dict.fromkeys(('key', 'value'), 2)
    print(d1 == d2 == d3 == d4)

    # key must be hashable
    d5 = {}
    for item in range(1, 1000):
        d5[item] = item ** 2
    print(len(d5))

    # pop
    d3.pop('key')

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib_gen = fibonacci()
print(next(fib_gen))  # 0
print(next(fib_gen))  # 1
print(next(fib_gen))  # 1
print(next(fib_gen))  # 2
print(next(fib_gen))  # 3

# ── Coroutines example - lazy list generator ─────────────────────────────────

def lazy_list_generator():
    i = 0
    while True:
        try:
            value = yield i
            i += 1
            print(value, i)
        except ValueError as e:
            print(e.args[0])

gen = lazy_list_generator()
next(gen)  # Start the coroutine
for i in [9, 7, "foo"]:
    gen.send(i)  # Send values to the coroutine

# ── Trampoline example - optimizing recursive Fibonacci calculation ─────────

def fib_trampoline(n):
    def fib_recursive(index=0, current=0, next=1):
        nonlocal index
        index += 1
       