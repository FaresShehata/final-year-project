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
import types
import urllib.request as request
from concurrent.futures import ThreadPoolExecutor
from functools import partial, reduce
from inspect import getfullargspec
from operator import itemgetter
from random import choice, randint
from re import subn
from sys import stderr, stdout
from timeit import Timer
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    Union,
)
from traceback import format_exception_only
from weakref import WeakValueDictionary


def seed_05() -> None:
    """seed 05 - concurrency"""
    print(">>> seed 05 <<<")

    # ----------------------------------------------------- #
    #               parallel processing                    #
    # ----------------------------------------------------- #

    def foo(x: int) -> None:
        print(f"{x} {foo.__name__}")

    with ThreadPoolExecutor(max_workers=2) as pool:
        for _ in range(3):
            pool.submit(foo, x=randint(1, 10))

    # ----------------------------------------------------- #
    #                   processPool                        #
    # ----------------------------------------------------- #

    workers = []
    for i in range(5):
        worker = multiprocessing.Process(target=foo, args=[i])
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()

    # ----------------------------------------------------- #
    #         concurrency and cancellation                  #
    # ----------------------------------------------------- #

    class Foo(threading.Thread):
        def run(self) -> None:
            while True:
                pass

        def cancel(self) -> bool:
            return self._stop.set()

        @property
        def stop(self) -> threading.Event:
            if not hasattr(self, "_stop"):
                self._stop = threading.Event()
            return self._stop

    f = Foo()
    f.start()
    f.cancel()
    f.join(timeout=1.0)

    # ----------------------------------------------------- #
    #                 atomic operations                     #
    # ----------------------------------------------------- #

    class Foo(object):

        x: int

        def __init__(self, x: int) -> None:
            self.x = x

        def inc_x(self) -> None:
            self.x += 1

        def dec_x(self) -> None:
            self.x -= 1

    obj = Foo(0)
    with threading.Lock():
        obj.inc_x()
        obj.dec_x()
    assert obj.x == 0

    # ----------------------------------------------------- #
    #     multiple threads running on the same object      #
    # ----------------------------------------------------- #

    class Bar(threading.Thread):
        x: int

        def __init__(self, x: int) -> None:
            super().__init__()
            self.x = x

        def run(self) -> None:
            for _ in range(randint(1, 3)):
                self.x += 1
            print(f"{self.name}: {self.x}")

    objs = [Bar(i * 10 + j) for i in range(1, 4) for j in range(1, 4)]
    for obj in objs:
        obj.start()
    for obj in objs:
        obj.join()

    # ----------------------------------------------------- #
    #           global variables in multiple processes      #
    # ----------------------------------------------------- #

    class Foo(threading.Thread):
        @classmethod
        def work(cls, x: int) -> List[int]:
            result: List[int] = []
            for _ in range(x):
                result.append(randint(1, 10))
            return result

        def __init__(self, x: int) -> None:
            super().__init__()
            self.x = x

        def run(self) -> None:
            results = self.work(self.x)
            print(f"{self.name}: work completed")
            print(f"{'.'.join(map(str, results))}")

    p1 = Foo(10)
    p2 = Foo(10)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def seed_05a() -> None:
    """seed 05 - concurrency (asyncio, asyncio.Queue, websockets, async generators)"""
    print(">>> seed 05a <<<")

    # ----------------------------------------------------- #
    #              async generator                         #
    # ----------------------------------------------------- #

    async def coroutine_generator() -> Generator[str, None, None]:
        yield "first"
        yield "second"

    async def main() -> None:
        async for value in