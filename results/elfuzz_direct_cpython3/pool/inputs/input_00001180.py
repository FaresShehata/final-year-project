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

    # template strings
    print(f'{"Hello":>10} {"world."}')

    # f-strings - dictionary lookup
    d = {'name': 'Alice'}
    name = d.get('name')
    print(name)

    # f-strings - multiple expressions
    print(f'{2+3} is the answer')

    # f-strings - formatted string literals
    print(f'{{1}} {{2}}'.format(1, 2))

    # f-strings - expression bodied function
    print(f'the answer is {lambda x: x*x(x): int}')
    print(f'the answer is {(lambda x: x*x)(int)}')

    # literal evaluation
    print(ast.literal_eval('1'))
    print(ast.literal_eval('[1, 2, 3]'))

    # escape sequences
    print(r"\n")

    # string formatting
    print(format(42, '%d'))
    print('{:.3f}'.format(3.141592653589793))
    print('Hello {} {}'.format('World!', 'Universe!'))


def _test_list():
    print('type: list')

    # constructor
    l1 = []
    l2 = [1, 2, 3, 4]
    l3 = list()

    # indexing
    a = [1, 2, 3][1:]
    b = [1, 2, 3][-1:]

    # slicing
    c = [1, 2, 3][:2]
    d = [1, 2, 3][::-1]
    e = [1, 2, 3][::2]

    # concatenation
    f = [1, 2, 3] + [4, 5, 6]

    # repetition
    g = ([1]*3)*4

    # list comprehensions
    h = [str(i) for i in range(10)]
    i = [bool(v) for v in [0, False]]
    j = [bool(v) for v in []]
    k = [bool(None) for v in [1]]

    # mixed assignment
    l = [1, 2]
    m = [3, 4]
    l += m
    l.extend(m)

    # reversed iteration
    l = [1, 2        return

    class FooBar:
        def bar(self, x: float) -> bool:
            return True

    # rich comparison
    a = 3 > 1 and not 2 < 0 or -1 >= 0
    print(a)

    # bitwise
    a = 0b111011 & 0b101011 >> 1 | 0b000100 << 2 ^ 0b111111 // 7 % 2
    print(a)

    # binary operations
    a = 1 + 2 * 3 - 4 / 5 ** 6
    print(a)

    # ternary operator
    a = 1 if 2 else 2
    print(a)

    # slicing
    a = [1, 2, 3]
    a[::2] = []
    del a[-1]

    # list comprehension
    nums = range(1, 11)
    squares = [x**2 for x in nums]
    print(squares)

    # dictionary comprehension
    pairs = [(i, i*2) for i in nums]
    nums_dict = {i: v for i, v in pairs}
    print(nums_dict)

    # set comprehension
    a = {v**2 for v in nums}
    print(a)


def _test_seq():
    print('type: sequence')
    seqs = ['foo', 1, 'bar', 2.0, ('baz',), 3]
    for e in seqs:
        print(type(e))

    # container protocols
    print(isinstance(seqs, Sequence))
    seq_iter = iter(seqs)
    print(isinstance(seq_iter, Iterable))
    print(isinstance(seq_iter, Iterator))
    # collection protocol
    print(all([True]))
    print(any([False]))
    print(len(seqs))
    print(max(seqs))
    print(min(seqs))
    print(sum(seqs))


def _test_tuple() -> tuple[int, ...]:
    print('type: tuple')
    t = (1,) + (2,)
    ts = 1, 2, 3
    print(ts)
    print(t + (4,))
    print((t + (4,))*3)
    print(tuple(range(10)))
    print(tuple(i*i for i in range(10)))
    print(tuple(str(i) for i in range(10)))

    # unpacking
    n1, n2 = 1, 2
    n1, *_ = (1, 2, 3)
    n1, n2, *_ = (1, 2, 3)
    _, n2, *_ = (1, 2, 3)
    n1, n2, *_ = (1, 2, 3, 4)
    print(n1, n2)

    # star unpack