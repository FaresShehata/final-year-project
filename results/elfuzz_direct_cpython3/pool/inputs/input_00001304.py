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
import io
import marshal
import multiprocessing.pool
import os
import pickle
import platform
import random
import re
import signal
import struct
import sys
import traceback
import types
import typing as t
from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from itertools import islice, zip_longest
from numbers import Number
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from queue import Queue
from shutil import copyfileobj
from statistics import mean
from string import ascii_letters, digits
from tempfile import TemporaryFile
from threading import Thread
from timeit import default_timer as timer
from types import CodeType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
)
from unittest.mock import patch, Mock
from warnings import warn


def _test() -> None:
    global x, y, z
    from seed_01 import A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, TEST, TEST2, TEST3, TEST4, TEST5, TEST6, TEST7, TEST8, TEST9, TEST10, TEST11, TEST12, TEST13, TEST14, TEST15, TEST16, TEST17, TEST18, TEST19, TEST20, TEST21, TEST22, TEST23, TEST24, TEST25, TEST26, TEST27, TEST28, TEST29, TEST30, TEST31, TEST32, TEST33, TEST34, TEST35, TEST36, TEST37, TEST38, TEST39, TEST4