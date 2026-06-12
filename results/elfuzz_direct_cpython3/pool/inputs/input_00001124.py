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


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float


# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)

# ── Custom type aliases ──────────────────────────────────────────────────────-

T1                     = TypeVar("T1")
T2                     = TypeVar("T2", bound=numbers.Number)


class MyInt(int):
    pass


class MyFloat(float):
    pass


MyNumber: TypeAlias = "float | int"
"""A generic number."""


# ── Typing Extras ────────────────────────────────────────────────────────────

FormattableString: TypeAlias = "str | Formatter"


class Formatter(textwrap.Formatter):
    argnum: int
    fmtstr: FormattableString


# ── Context managers ──────────────────────────────────────────────────────────

@contextlib.contextmanager
def suppress(*exc_types):
    with contextlib.suppress(*exc_types):
        yield


@contextlib.contextmanager
def redirect_stdout(out: io.StringIO):
    old = sys.stdout
    sys.stdout = out
    try:
        yield
    finally:
        sys.stdout = old


# ── Numbers ABIs ────────────────────────────────────────────────────────────

default_float_info = {
    "emax": 1023,
    "eps": 1e-9,
    "machep": -97,
    "minexp": -999,
    "mininvexp": -98,
    "minpos": 2.2250738585072014e-308,
    "max": 1.7976931348623157e+308,
    "maxexp": 1024,
    "precision": 15,
}


def new_float_info() -> dict[str, int]:
    info = default_float_info.copy()
    info["max"] *= 1.25**info["machep"]
    return info


class FloatInfo(new_float_info()):
    pass


f = FloatInfo(max=5.5)
print(f.max)


class FloatTypeInfo:
    max: int
    min: int
    eps: float

    def __init__(self, max: int, min: int, eps: float):
        self.max = max
        self.min = min
        self.eps = eps

    def __repr__(self):
        return f"{sum(map(ord, repr(self)))}"


fti = FloatTypeInfo(max=5, min=-5, eps=0.001)
print(fti)



# ── Multiprocessing ──────────────────────────────────────────────────────────

class Worker(multiprocessing.Process):

    def run(self) -> None:
        while True:
            msg = queue.get()
            if msg == 'exit':
                break
            print(msg)


w = Worker()

queue.put('Hello!')
time.sleep(1)
queue.put('Hi!')

queue.task_done()
queue.join()

with Pool(processes=8) as pool:
    result = pool.apply_async(math.sqrt, (16,))
    print(result.get())

pool.close()


# ── Python version ───────────────────────────────────────────────────────────
import platform

platform.python_version()

import sys

# Get major, minor, micro and release level
major, minor, micro, release_level = sys.version_info[:4]

# Check if Python is CPython implementation
is_cpython = sys.implementation.name == 'cpython'

# Print version information
print(f'Python Version: {sys.version}')
print(f'Major Version: {major}')
print(f'Minor Version: {minor}')


# ── JSON ─────────────────────────────────────────────────────────────────────

json_str = '{"a":1}'
json_obj = json.loads(json_str)

def parse_json(input_string: str) -> JsonValue:
    parsed = ast.literal_eval(input_string)
    return parsed

parsed = parse_json(json_str)

for key, value in parsed.items():
    print(key, value)


# ── Setuptools ───────────────────────────────────────────────────────────────

from setuptools import setup

setup(
    name="test",
    version='0.1',
    py_modules=["test"],
    entry_points={
        "console_scripts": ["test=test:cli"]
    }
)

# ── Typing extensions ────────────────────────────────────────────────────────


# ──          lambda calculus encoding, currying, partial application, trampolining, etc.
"""

import asyncio
from contextlib import asynccontextmanager
import re
import sys
from typing import List, Literal, NamedTuple, Optional, Tuple, TypeAlias, Union, get_args

sys.setrecursionlimit(500)

re.match(r"^(.+)(\d+)$", "hello")


@asynccontextmanager
async def context_manager():
    try:
        yield
    finally:
        print("Done!")


# https://docs.python.org/3/howto/functional.html?highlight=closure#closures
def func_closure():
    x = [1]
    def inner():
        x.append(2)
        return x[0]
    return inner


class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data) # kwargs unpacking
    
    
person_1 = Person('John', 28)
print(person_1.__dict__)

person_data = {"name": "Jane", "age": 45}
person_2 = Person.from_dict(person_data)
print(person_2.__dict__)


# @staticmethod vs. @classmethod
# Static methods don't receive instance as the first argument that's why they are useful when you want to
# you can access class attributes but not instance attributes.

class MyClass:

    @staticmethod
    def static_method(x):
        return x + 1

    @classmethod
    def class_method(cls, y):
        return cls.static_method(y)


MyClass().static_method(1)   # returns 2
MyClass().class_method(1)    # returns 2


# docstring
def my_function(param: int) -> None:
    """
    This is a function description.
    :param param: some integer parameter
    :type param: int
    """
    pass
help(my_function)


# type hinting
my_list: list[int] = []
my_tuple: tuple[str, ...] = ('Hello', 'World')
my_set: set[int] = {1}
my_dictionary: dict[str, int] = {'a': 1}


# assert
assert isinstance(1, int)
assert isinstance([1], list)


# unbound method
def foo(self=None, arg=None):
    if self is not None:
        # do something with `self`
        ...
    else:
        # use the default value of `arg` here
        ...

foo()
foo(arg=2)


if True:
    print("True")
else:
    print("False")

x = 1 if True else 0
y = 0 if False else 1

#