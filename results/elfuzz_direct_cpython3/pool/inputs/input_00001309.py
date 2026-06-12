"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
higher-order functions, generators, iterators, coroutines.

Some of these are taken from the excellent tutorial at https://realpython.com/.
"""

from collections import defaultdict
import random as rnd
from itertools import chain
import operator
from functools import wraps, partial, update_wrapper
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Hashable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
    final,
)
import copyreg
import dataclasses
import decimal
import enum
import functools
import gc
import heapq
import itertools
import math
import operator
import os
import pickle as pkl
import queue
import re
import secrets
import signal
import string
import subprocess
import sys
import threading
import time
import types
import unicodedata
import weakref
from contextlib import contextmanager
from multiprocessing.synchronize import Event as MPEvent
from queue import Empty as QueueEmptyError
from statistics import mean
from types import FrameType, TracebackType
from typing_extensions import Literal, ParamSpec, Self
from urllib.parse import urlparse
from weakref import ref


# ── Functional programming basics ─────────────────────────────────────────────

ZERO     = 0
ONE      = 1
MAX_INT  = sys.maxsize
MIN_INT  = -sys.maxsize - 1
NEG_ONE  = -1
POS_ONE  = +1
PI       = 3.141592653589793
E        = 2.718281828459045
LN_2     = 0.6931471805599453
LOG_2    = 1 / LN_2
SQRT_PI  = 1.7724538509055160272981674833411451827975494561223871282138077192908625696
SQRT_2   = 1.41421356237309504SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


@curry
def fold_str(sep: str, left: str, right: str) -> str:
    return f"{left}{sep}{right}"


def compose(*fns: Callable) -> Callable:
    """Right-to-left function composition."""
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed


add3_curried = curry(add3)
print(
    fold_str(" ", "(", ")"),
    add3_curried(1)(2)(3),
)


# ── Higher-order functions ───────────────────────────────────────────────────-

def mymap(fn: Callable[[Any], Any], args: list[Any]) -> list[Any]:
    return [fn(arg) for arg in args]


def map_wrap(fn: Callable[[Any], Any]):
    def inner(args: Iterable[Any]) -> list[Any]:
        return list(map(fn, args))
    return inner


lmap = map_wrap(list)
imap = map_wrap(iter)
filter_map = partial(map_wrap, filter)

lfilter = map_wrap(filter)
imap_filter = partial(imap, filter)

def myzip(*args: Iterable[Any]) -> list[tuple[Any]]:
    iterators = tuple(map(imap, args))
    while True:
        yield tuple(iterator.pop() for iterator in iterators)


zipped = myzip([1, 2, 3], ["a", "b", "c"])
for item in zipped:
    print(item)


# ── Decorators ───────────────────────────────────────────────────────────────

def debug(decorated_fn: Callable) -> Callable:
    @wraps(decorated_fn)
    def wrapper(*args, **kwargs):
        print(f"Calling {decorated_fn.__name__} with {args}, {kwargs}")
        result = decorated_fn(*args, **kwargs)
        print(f"{decorated_fn.__name__} returned {result}")
        return result
    return wrapper


class DelegatingCallable(object):

    def __init__(self, method_name: str, delegate_method_name: str):
        self.delegate = getattr(self, delegate_method_name)
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        return getattr(self.delegate, self.method_name)(*args, **kwargs)


class LoggingCallableMixin:

    def call_with_logging(self, *args, **kwargs):
        print(f"Calling {self.method_name} with {args}, {kwargs}")
        result = self.call(*args, **kwargs)
        print(f"{self.method_name} returned {result}")
        return result

    call = DelegatingCallable("call", "call_with_logging")


class DebuggableLoggingCallable(LoggingCallableMixin, object):

    def __init__(self, fn: Callable):
        self.fn = fn

    def __getattr__(self, name):
        attr = getattr(self.fn, name)
        if callable(attr):
            func = DelegatingCallable(name, attr.__name__)
            update_wrapper(func, attr)
            setattr(self, name, func)
        return attr


debug_decorator = DebuggableLoggingCallable(debug)
my_add3_debug = debug_decorator(add3)

assert my_add3_debug(1)(2)(3) == add3(1, 2, 3)


# ── Coroutines and generators ─────────────────────────────────────────────────

async def coroutine():
    pass


class GeneratorAsyncIterator(Generic[T], AsyncIterable[T]):
    
    def __init__(self, gen: Coroutine):
        self.gen = gen
    
    def __aiter__(self) -> GeneratorAsyncIterator:
        return self
    
    async def __anext__(self):
        try:
            value = await self.gen.send(None)
        except StopIteration as e:
            raise StopAsyncIteration from e
        else:
            return value


class GeneratorCoroutine(Generic[R], AsyncGenerator[R, None]): 
    
    def __init__(self, gen: Callable[[], R]):
        self.gen = gen()
    
    async def __anext__(self):
        return await self.gen.__anext__()
    
    async def ac
def run_and_inspect(fn: types.FunctionType) -> types.FrameType:
    frame = inspect.currentframe().f_back
    inspector = FrameInspector(frame)

    # See https://docs.python.org/3/library/dis.html#dis.showcode
    dis.setnextinstruction(inspector.visit)
