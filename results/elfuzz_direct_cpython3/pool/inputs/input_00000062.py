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
    num_threads = 20
    total_sum = 1_000_000

    # Create a lock to synchronize access to the shared variable
    lock = threading.Lock()
    shared_var = 0

    def worker(num):
        for _ in range(total_sum):
            # Acquire the lock before modifying the shared variable
            with lock:
                shared_var += 1 / num_threads

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i + 1,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert round(shared_var, 3) == round(total_sum / num_threads, 3)


@pytest.mark.parametrize("func", [sum, max])
def test_lock(func):
    """Test locking with functions."""
    dummy_list = list(range(10))
    expected_result = func(dummy_list)

    with contextlib.ExitStack() as stack:
        locks = [stack.enter_context(threading.Lock()) for _ in range(len(dummy_list))]
        result = func([locks[i], dummy_list[i]] for i in range(len(dummy_list)))

    assert result == expected_result


def test_signal_handler():
    """Test signal handling."""

    def my_function(x: int, y: int):
        return x * y

    print(my_function(1, 2))
    print(my_function.__name__)
    print(type(my_function))

    try:
        raise ValueError("oops")
    except ValueError as e:
        print(e.args[0])


def test_thread_join_timeout():
    """Test join timeout"""
    first_thread = threading.Thread(
        target=lambda: time.sleep(1.0), name="first_thread"
    )
    second_thread = threading.Thread(
        target=lambda: time.sleep(2.0), name="second_thread"
    )
    first_thread.start()
    second_thread.start()
    try:
        first_thread.join(timeout=2.0)
        second_thread.join(timeout=2.0)
    finally:
        first_thread.join()
        second_thread.join()


def test_multiprocessing():
    """Test multiprocessing."""
    num_processes = 8
    results_queue = queue.Queue()

    class WorkerProcess(multiprocessing.Process):
        def run(self