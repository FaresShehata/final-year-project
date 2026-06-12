"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import collections.abc as c_abc
import functools
import inspect
import operator
import os
import platform
import random
import reprlib
import re
import signal
import stat
import string
import subprocess
import sys
import threading
import traceback
import types
import warnings
from abc import ABCMeta, abstractmethod
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from email.message import Message
from itertools import chain, cycle, islice, repeat, tee
from math import e, pi
from numbers import Number
from pathlib import Path
from pprint import PrettyPrinter
from queue import Empty, Queue
from re import Pattern
from statistics import mean
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Generator,
    Iterable,
    List,
    Literal,
    Mapping,
    Match,
    NoReturn,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
)

from _pytest.outcomes import Fail
from pytest_bdd import given, parsers, then
from requests import Response

from seed01 import (
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    I,
    J,
    K,
    L,
    M,
    N,
    O,
    P,
    Q,
    R,
    S,
    T,
    U,
    V,
)
from seed02 import a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v


def print_seed_values():
    """
      54638709245678134567892456789
    >>> from seed04 import *
    >>> print_seed_values()
    """

    print(f"{a} {b} {c} {d} {e} {f} {g} {h} {i} {j} {k} {l} {m} {n} {o} {p} {q} {r} {s} {t} {u} {v}")


# noinspection PyShadowingBuiltins
def assert_equals(expected: