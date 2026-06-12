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

        def set_x(self, x: int) -> None:
            self.x = x

        def increment_x(self) -> None:
            self.x += 1

        def add_x(self, x: int) -> None:
            self.x += x

        def decrement_x(self) -> None:
            self.x -= 1

        def subtract_x(self, x: int) -> None:
            self.x -= x

    a = Foo(randint(1, 10))
    b = Foo(a.x + randint(1, 10))

    with ThreadPoolExecutor(max_workers=2) as pool:
        future_a = pool.submit(Foo.increment_x, obj=a)
        future_b = pool.submit(b.add_x, x=b.x + randint(1, 10))

        result_a = future_a.result()
        result_b = future_b.result()

    print(result_a)
    print(result_b)