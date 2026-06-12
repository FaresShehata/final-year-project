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
    Iterable,
    List,
    Mapping,
    NamedTuple,
    NewType,
    NoReturn,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    TypeAlias,
    TypeGuard,
    TypedDict,
    Union,
    runtime_checkable,
)
from types import FrameType, TracebackType
from unittest.mock import patch
from weakref import ref


def _test_thread_join_timeout() -> None:
    # The thread terminates before the timeout expires.
    def target():
        print("target started")
        time.sleep(1)
        print("target terminated")

    with threading.Thread(target=target) as t:
        t.start()

        try:
            t.join(timeout=2)
            assert False, "Thread did not terminate"
        except TimeoutError:
            pass


def _test_thread_is_alive() -> None:
    # Thread is alive.
    def target():
        print("target started")
        time.sleep(1)

    with threading.Thread(target=target) as t:
        t.start()
        assert t.is_alive()


def _test_thread_ident() -> None:
    # Thread identifier is same for all threads in a process.
    def target():
        print(f"target {os.getpid()} started")
        time.sleep(1)

    with threading.Thread(target=target) as t1:
        t1.start()
        print(t1.ident)

        with threading.Thread(target=target) as t2:
            t2.start()
            print(t2.ident)


def _test_thread_schedule_start() -> None:
    # The thread begins executing immediately after it starts.
    def target():
        print("target started")

    with threading.Thread(target=target) as t:
        t.start()
        print("main thread terminating")


def _test_thread_chain_termination() -> None:
    # Termination of one thread can affect another.
    def target1(sleep_duration):
        time.sleep(sleep_duration)
        return sleep_duration

    def target2(sleep_duration):
        time.sleep(sleep_duration)
        return sleep_duration

    with threading.Thread(target=target1, args=(3,)) as t1:
        t1.start()

        with threading.Thread(target=target2, args=(5,), daemon=True) as t2:
            t2.start()

            t1.join(timeout=3)
            if not t1.is_alive():
                assert True
            else:
                assert False


# TODO: make this