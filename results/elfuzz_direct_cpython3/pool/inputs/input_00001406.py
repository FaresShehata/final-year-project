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
    TypeGuard,
    TypedDict,
    Union,
)
from types import TracebackType
from abc import ABCMeta, abstractmethod
from collections.abc import Generator, Iterable
from io import TextIOBase, BytesIO
from re import Match
from sys import stdout, stderr
from typing_extensions import TypeAlias, get_args, get_origin


def is_pair(x: object) -> bool:
    return isinstance(x, tuple) and len(x) == 2


def is_triple(x: object) -> bool:
    return isinstance(x, tuple) and len(x) == 3


class MyPair(Generic[T1, T2]):
    def __init__(self, x: T1, y: T2):
        self.x = x
        self.y = y


class MyTriple(Generic[T1, T2, T3]):
    def __init__(self, x: T1, y: T2, z: T3):
        self.x = x
        self.y = y
        self.z = z


# TODO: do the same for other built-ins
A: int | str | bytes = "str"  # type: ignore[assignment]
B: int | str | bytes = 27
C: int | str | bytes = b"\x00\x01"
D: int | str | bytes = bytearray([98, 121, 83])
E: int | str | bytes = memoryview(b"example")
F: int | str | bytes = range(1, 11)

G: complex = 1 + 2j
H: complex = -1j
I: complex = 3e-10j
J: complex = 0b111_0001_1100_0101j
K: complex = 0o111_0001_1100_0101j
L: complex = 0x1FF_FFEE_FFFF_FFFF_EEEE_FC00j
M: complex = -0b001_0001_1001_0110j
N: complex = -0o001_0001_1001_0110j
O: complex = -0x001_FFEE_FFFF_FFFF_EEEE_FC00j

P: float = 1.23
Q: float = 1.
R: float = -1.23
S: float = 1.23456789123456789
T: float = -1.23456789123456789
U: float = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
V: float = -3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679

W: bool = True
X: bool = False
Y: bool = not W
Z: bool = not X


class Point:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @property
    def distance(self) -> float:
        return ((self.x ** 2) + (self.y ** 2)) ** 0.5

    def distance_to_point(self, point: Point) -> float:
        return (((point.x - self.x) ** 2) + ((point.y - self.y) ** 2)) ** 0.5

    def distance_to_x_axis(self) -> float:
        return abs(self.y)


p1 = Point(0, 10)
assert p1.distance == 10
assert p1.distance_to_point(Point(-1