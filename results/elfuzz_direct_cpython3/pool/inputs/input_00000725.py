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

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


UserKeys: TypedDict = {
    "id":   int,
    "name": str,
}


# ── ParamSpec ────────────────────────────────────────────────────────────────

def func(**kwargs: type[Any]):
    ...


ParamSpecKwargs: ParamSpec["Kwargs"]


def func(**kwargs: Kwargs) -> None:
    ...


func(name=str, age=int)


# ── GetTypeHints ────────────────────────────────────────────────────────────

def get_type_hints_with_annotations(func: Callable[P, T]) -> dict[str, type[Any]]:
    return get_type_hints(func, globalns=func.__globals__)


get_type_hints_with_annotations(get_type_hints_with_annotations)
# {'func': <class 'function'>}

# ─── RevealType Stub ────────────────────────────────────────────────────────

reveal_type(123)
reveal_type("hello world")
reveal_type([1, 2, 3])
reveal_type(UserRecord())
reveal_type(UserKey(name=str))

reveal_type(str.split())
reveal_type((lambda x: True)(x))
reveal_type(lambda x: x + 1(x))


# ── ContextLib ──────────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*types, **exc_info) -> Generator[None, None, None]:
    yield


with suppress(AttributeError):
    raise AttributeError()

with suppress(ValueError), suppress(IndexError):
    pass

with suppress(ValueError, IndexError):
    pass

with suppress(AttributeError, ValueError, KeyError):
    pass

with suppress(AttributeError, BaseException), suppress(BaseException):  # noqa
    pass

with suppress(Exception):
    try:
        raise RuntimeError()
    except Exception:
        pass

with suppress(TypeError, IsADirectoryError):
    pass

with suppress(TypeError, IsADirectoryError), suppress(FileNotFoundError):
    pass

try:
    ...
except EOFError:
    pass
except KeyboardInterrupt:
    pass
except (EOFError, KeyboardInterrupt):
    pass

try:
    ...
except (EOFError, KeyboardInterrupt):
    pass

try:
    ...
except EOFError, e:
    pass
except KeyboardInterrupt, e:
    pass
except (EOFError, KeyboardInterrupt), e:
    pass

try:
    ...
except (EOFError, KeyboardInterrupt) as e:
    pass

try:
    ...
except (EOFError, KeyboardInterrupt):
    pass

with suppress(
    OSError,
    IOError,
    TypeError,
    ValueError,
    ZeroDivisionError,
    FileNotFoundError,
    LookupError,
    NotADirectoryError,
    PermissionError,
    FileExistsError,
    InterruptedError,
    BlockingIOError,
    ChildProcessError,
    TimeoutError,
    ConnectionError,
    ConnectionAbortedError,
    ConnectionRefusedError,
    ConnectionResetError,
    BrokenPipeError,
    FileExistsError,
    URLError,
    socket.error,
    struct.error,
    MemoryError,
    RecursionError,
    NotImplementedError,
    ArithmeticError,
    AssertionError,
    AttributeError,
    BufferError,
    EOFError,
    EnvironmentError,
    ImportError,
    ModuleNotFoundError,
    NameError,
    UnboundLocalError,
    ReferenceError,
    RuntimeError,
    SyntaxError,
    IndentationError,
    TabError,
    SystemError,
    SystemExit,
    TypeError,
    UnicodeError,
    UnicodeDecodeError,
    UnicodeEncodeError,
    UnicodeTranslateError,
    Warning,
    BytesWarning,
    ResourceWarning,
    DeprecationWarning,
    FutureWarning,
    ImportWarning,
    PendingDeprecationWarning,
    RuntimeWarning,
    SyntaxWarning,
    UserWarning,
    DeprecatedWarning,
    DeprecationWarning,
    PendingDeprecationWarning,
    ResourceWarning,
    StopIteration,
    GeneratorExit,
    StopAsyncIteration,
    GeneratorExit,
    StopAsyncIteration,
    KeyError,
    IndexError,
    MemoryError,
    OverflowError,
    Reference@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


def pipe(*fns: Callable) -> Callable:
    """Left-to-right pipeline."""
    def piped(x):
        for f in fns:
            x = f(x)
        return x
    return piped


# ── Closures & factories ──────────────────────────────────────────────────────

def make_counter(start: int = 0, step: int = 1):
    state = [start]          # mutable cell avoids nonlocal for clarity

    def increment() -> int:
        v = state[0]
        state[0] += step
        return v

    def reset() -> None:
        state[0] = start

    def peek() -> int:
        return state[0]

    increment.reset = reset  # type: ignore[attr-defined]
    increment.peek  = peek   # type: ignore[attr-defined]
    return increment


def make_accumulator(init: float = 0.0) -> Callable[[float], float]:
    total = init

    def acc(x: float) -> float:
        nonlocal total
        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args

    def apply(self):
        return self.fn(*self.args)


def trampoline(thunk: Thunk) -> Any:
    while isinstance(thunk, Thunk):
        thunk = thunk.apply()
    return thunk


def delay(func: Callable) -> Thunk:
    return Thunk(func)


def lazy_adder(a: int, b: int) -> Thunk:
    return Thunk(add, a, b)


# ── Partial applications and lambdas ──────────────────────────────────────────

def partial(func: Callable, *positional_args: A) -> Callable:
    """
    Return a new callable with the given positional arguments pre-applied.

    >>> double = partial(operator.mul, 2)
    >>> triple = partial(operator.mul, 3)
    >>> square = partial(pow, 2)
    """

    def wrapped(*rest):
