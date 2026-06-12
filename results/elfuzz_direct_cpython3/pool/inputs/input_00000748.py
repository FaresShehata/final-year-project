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
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import trace
import tracemalloc as tm
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto
from functools import partial, reduce, singledispatchmethod
from itertools import accumulate
from operator import add
from pathlib import Path
from timeit import default_timer as timer
from typing import Any, Callable, ClassVar, Generic, Iterator, ParamSpec, TypeVar


def _seed1() -> None:
    """
    Seed 01 — Introduction to Python: standard library modules &
                built-in functions and classes
    """

    print("Seed 01")


def seed1():
    """Seed 01"""

    # Built-in functions and math module

    print(2 ** 3)
    print(bin(8))
    print(hex(9))
    print(int('10', base=2))
    print(round(3.1567, ndigits=2))

    print(abs(-123))
    print(max((1, -3, 4, 2), key=lambda x: abs(x)))
    print(min([1, 3, -2], key=lambda x: abs(x)))

    def f(x):
        return x * (x + 1)


    print(f(range(3)))
    help(print)

    from math import sqrt

    print(sqrt(4))
    print(dir(math))
    print(id(marshal))
    print(sys.modules['math'].sqrt)
    print(help(math.sqrt))
    print(math.pi)
    print(type(math.pi))
    print(math.pi.__module__)
    print(math.sin(0))
    print(math.tan(0))


def _seed2() -> None:
    """
    Seed 02 — Introduction to Python: exception handling; raising exceptions;
               assertions; finally blocks; context managers; try-except blocks;
               else clause; nested try-excepts; exception chaining;
               assert statements with custom error messages and symbols;
               __debug__,__traceback__, traceback.format_exc(), traceback.print_exc()
    """

    print("Seed 02")


def seed2():
    """Seed 02"""


# Exceptions

    # SyntaxError, IndentationError, TabError, EOFError, RuntimeError, StopIteration,
    # TypeError, ValueError, OverflowError, ZeroDivisionError, RecursionError,
    # AssertionError, AttributeError, BufferError, MemoryError, NameError, UnboundLocalError,
    # ReferenceError, RuntimeError, NotImplementedError, OSError, BlockingIOError, ChildProcessError,
    # ConnectionError, BrokenPipeError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError,
    # FileExistsError, FileNotFoundError, InterruptedError, IsADirectoryError, NotADirectoryError, PermissionError,
    #