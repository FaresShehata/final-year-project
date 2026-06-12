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
import itertools
import os.path
import sys
import types
import typing
import traceback
import unittest
import uuid
import warnings
import weakref
import zlib
import struct
import timeit
import zipfile
import zipimport
import textwrap
import math
import platform
import pickle
import cPickle
import marshal
import copy_reg as copyreg
import _weakrefset as wfs
import io
import re
import array
import collections
import collections.abc
import collections.abc._callableiterator
import datetime
import decimal
import fractions
import hashlib
import heapq
import hmac
import io
import itertools
import json
import keyword
import linecache
import logging
import mmap
import multiprocessing.pool
import operator
import pathlib
import pprint
import random
import reprlib
import signal
import sqlite3
import stat
import string
import subprocess
import sysconfig
import threading
import time
import token
import tokenize
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import warnings
import weakref
import xmlrpc.client
import sysconfig
import asyncio
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import asyncio.run_as_future
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio."""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    TypeVar,
    overload,
    runtime_checkable,
)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
U = TypeVar("U")

# ---------------------------------------------------------


class PriorityQueue(Generic[K, V]):
    """Priority Queue implementation.

    >>> pq = PriorityQueue()
    >>> pq.push(1, 'a')
    >>> pq.push(3, 'b')
    >>> pq.push(5, 'c')
    >>> pq.pop()
    ('b', 3)
    """

    def __init__(self) -> None:
        self._queue: list[tuple[int, K]] = []
        self._index: dict[K, int] = {}

    def push(self, key: K, val: V) -> None:
        if key in self._index:
            raise ValueError(f"Duplicate key: {key}")
        entry = (val, self._max_priority(), key)
        self._index[key] = len(self._queue)
        self._queue.append(entry)
        self.heapify()

    @overload
    def pop(self) -> tuple[Literal["", "value"], K]:
        ...

    @overload
    def pop(self) -> tuple[Literal["priority"], K]:
        ...

    def pop(self) -> tuple[str, K]:
        _, priority, key = self._queue.pop(0)
        del self._index[key]
        return ("value", key), priority

    def heapify(self) -> None:
        heapq.heapify(self._queue)

    @property
    def max_priority(self) -> K:
        try:
            _, priority = self._queue[-1]
            return priority
        except IndexError:
            raise ValueError("Empty queue") from None

    def peek(self) -> tuple[V, K]:
        _, value, key = self._queue[-1]
        return value, key

    def is_empty(self) -> bool:
        return not self._queue

    def update_priority(
        self, old_key: K, new_val: V, *, priority_type: str = ""
    ) -> None:
        index = self._index.get(old_key)
        if index is None:
            raise KeyError(f"{old_key} not found")
        entry = self._queue[index]
        _old_priority, _old_value, _old_key = entry
        _new_priority = (
            min(self.max_priority, _old_priority),
            max(-_old_priority, _old_priority),
        )
        new_entry = (_new_priority, new_val, old_key)
        self._queue[index]