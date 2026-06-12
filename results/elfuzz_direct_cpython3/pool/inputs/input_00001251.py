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
    b: int = 2
    assert a == b, "a != b"

    # type hints
    def foo(a: int) -> None:
        return

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
    _, n1, *_, n2 = (1, 2, 3)
    *n1, n2 = (1, 2, 3)
    n1, *_, n2 = (1, 2, 3)
    *n1, n2, *_ = (1, 2, 3)
    print(n1, n2)

    # copy
    tup = (1, 2)
    t2 = tup
    del tup
    print(t2)
    tup = tuple([1, 2])
    t2 = tup[:]
    print(tup, t2)

    # immutability
    t = (1, 2, 3)
    try:
        t[0] = 4
    except TypeError:
        print('TypeError')

    # slice assignment
    t = (1, 2, 3)
    t[:2] = reversed(t[:2])
    print(t)
    t[:2] = ()
    print(t)

    # index syntax
    t = (1, 2, 3)
    print(t.index(2))
    print(t.count(2))

    # hash
    t = (1, 2, 3)
    h = hash(t)
    print(hash(t))
    print(h)

    # pickle
    print(repr(cast(int, pickle.loads(pickle.dumps(1)))))
    print(repr(cast(float, pickle.loads(pickle.dumps(1.0)))))
    print(repr(cast(dict[str, int], pickle.loads(pickle.dumps({'key': 1})))))
    print(repr(cast(list[int], pickle.loads(pickle.dumps([1])))))


def _test_list() -> list[int]:
    print('type: list')
    l = [1, 2, 3]
    ll = list(l)
    l.append(4)
    l.insert(0, 0)
    l.extend(ll)
    l.pop()
    l.remove(2)
    l.clear()
    l.reverse()
    l.sort()

    # concat
    l += range(10)
    # equal to l.extend(range(10))
    l.extend(range(10))

    # extend
    l.extend('hello')

    # insert
    l.insert(0, 'start')

    # remove
    l.remove('hello')

