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
    print(">>> threadpool")
    # threadpools = [multiprocessing.Pool(1) for _ in range(3)]
    threadpools = [ThreadPoolExecutor(max_workers=2) for _ in range(3)]

    def some_work(n: int) -> str:
        return f"result of {n}"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(some_work, range(10)))
        assert all([r.startswith("result of") for r in results])

    # TODO: backoff

    def foo():
        ...

    def bar():
        ...

    t1 = Thread(target=foo)
    t2 = Thread(target=bar)

    t1.start()
    t2.start()

    t1.join(timeout=5.0)
    t2.join(timeout=5.0)

    def baz(i):
        for j in range(10):
            yield i * j

    gen = baz(17)
    while True:
        try:
            val = next(gen)
        except StopIteration as ex:
            break
        else:
            print(val)

    def _sleep(seconds: float) -> None:
        time.sleep(seconds)

    with ThreadPoolExecutor(max_workers=2) as pool:
        future1 = pool.submit(_sleep, 1)
        future2 = pool.submit(_sleep, 2)
        for future in [future1, future2]:
            result = future.result()
            print(result)

    sleep_results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(_sleep, seconds + randint(-1, 1))
            for seconds