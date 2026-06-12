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
import functools
import inspect
import itertools
import logging
import math
import mmap
import multiprocessing as mp
import operator

from typing import Any, Callable, Dict, Iterable, Iterator, List, NoReturn, Optional, Tuple, TypeVar, Union, cast

from .utils import (
    AnnotationType,
    ConcreteAnnotationType,
    _array_ctype,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ── Caching ───────────────────────────────────────────────────────────────────

T = TypeVar("T")
U = TypeVar("U")


def cached_property(fn: Callable[..., T]) -> property:
    """A property that caches its results."""
    attr_name = "_" + fn.__name__

    @property
    def wrapped(self) -> T:
        try:
            return getattr(self, attr_name)
        except AttributeError:
            value = fn(self)
            setattr(self, attr_name, value)
            return value

    return wrapped


@cached_property
def is_threaded() -> bool:
    return threading.active_count() > 1


@cached_property
def has_mmap_module() -> bool:
    """Check the availability of the `mmap` module.
    """
    try:
        import mmap   # noqa: F401
    except ImportError:
        return False
    return True


@cached_property
def is_windows() -> bool:
    """Determine if we're on a Windows machine.

    This function checks the OS name and version to determine if we're running
    under Windows. If you need more information about the current operating
    system, use the platform module instead.
    """
    return os.name == "nt"


@cached_property
def is_posix() -> bool:
    """Determine if we're on a POSIX-compliant Unix-like operating system.

    This function checks the OS name to determine if we're running under a
    POSIX-compatible Unix-like system. It does not guarantee that the system
    will be POSIX compliant (e.g., macOS). Use platform.system instead for a
    more comprehensive check.
    """
    return os.name == "posix" or sys.platform.startswith("linux") \
           or sys.platform.startswith("darwin") or sys.platform.startswith("cygwin")


@cached_property
def is_macos() -> bool:
    """Determine if we're on macOS."""

    if sys.platform.startswith('linux') and 'Darwin' in platform.mac_ver()[0]:
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
        result = f(*args)
        while isinstance(result, Thunk):
            result = result.fn(*result.args)
        return result
    return wrapper


def _even_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return acc
    return Thunk(_odd_tc, n - 1, acc)


def _odd_tc(n: int, acc: bool) -> "bool | Thunk":
    if n == 0:
        return not acc
    return Thunk(_even_tc, n - 1, acc)


is_even_tc = trampoline(lambda n: Thunk(_even_tc, n, True))


# ── Generator coroutines (send / throw / close) ───────────────────────────────

def running_average() -> Generator[float, float, str]:
