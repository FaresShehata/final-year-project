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
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

import pytest

# pylint: disable=too-many-lines


def test_threading():
    """Test thread synchronization with shared data."""
    sema = threading.Semaphore(2)
    running = False
    queued = 1
    done = 0
    try:
        print("Starting")
        t1 = threading.Thread(target=lambda: _worker(sema, "A"))
        t2 = threading.Thread(target=lambda: _worker(sema, "B"))
        t3 = threading.Thread(target=lambda: _worker(sema, "C"))
        t4 = threading.Thread(target=lambda: _worker(sema, "D"))
        t1.start()
        t2.start()
        t3.start()
        t4.start()

        while True:
            if not any((t.is_alive() for t in [t1, t2, t3, t4])):
                break
            time.sleep(0.01)
        assert done == 4 and queued == 2 * 4 - 4 + 2
    finally:
        print("Stopping")
        t1.join()
        t2.join()
        t3.join()
        t4.join()


def _worker(sema: threading.Semaphore, name: str):
    global running, queued, done
    if not running:
        running = True
        print(f"Started {name}")
    else:
        if queued >= 8:
            return
        queued += 1
    try:
        sema.acquire(timeout=20)
        print(f"{name} got the lock")
        time.sleep(secrets.random_int(min=1, max=2))
        sema.release()
        print(f"{name} released the lock")
    except Exception as e:
        print(e)
    else:
        print(f"{name} finished")
        done += 1


@pytest.mark.skip(reason="temporary skip due to flaky behaviour on CI")
def test_concurrent_futures():
    """Test concurrency using an executor."""
    nthreads = 4
    threads = []
    results = []

    def worker(n: int):
        results.append(n**n)

    # Use a pool of workers so that we can run several tasks concurrently.
    with ThreadPoolExecutor(max_workers=nthreads) as executor:
        futures = list(executor.map(worker, range(nthreads)))
        assert len(futures) > 0

    assert sorted(results) == [i**i for i in range(nthreads)]


def test_multiprocessing():
    """Test multiprocessing."""
    def _worker(name: str):
        time.sleep(secrets.randbelow(10))
        return name + " is done"

    p = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    result = p.apply_async(_worker, ("foo",))
    assert result.get() == "foo is done"
    result = p.apply_async(_worker, ("bar",))
    assert result.get() == "bar is done"


class TestClassGetItem:

    def test_setitem(self):
        class Foo:
            pass
        f = Foo()
        f["x"] = 42
        assert f.x == 42
        f["y"] = lambda x: x ** x
        assert f.y(2) == 4
        del f["x"]
        assert "x" not in f.__dict__

    def test_class_getitem(self):
        class Bar(Foo):
            def __getitem__(self, index):
                return self.__