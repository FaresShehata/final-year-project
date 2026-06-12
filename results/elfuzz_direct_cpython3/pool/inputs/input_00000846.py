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
import pickle
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tokenize
import traceback
import unittest.mock as mock
import weakref
from collections.abc import Callable, Hashable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from html.parser import HTMLParser
from inspect import Parameter, signature
from itertools import chain
from logging import Logger
from math import isclose, log10
from operator import add, mul
from pathlib import Path
from queue import Queue
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Final,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)
from urllib.parse import quote_plus
from uuid import UUID
from warnings import warn

# TODO: https://peps.python.org/pep-0672/#convention-over-configuration
from _pytask.config import hookimpl


def decorator(*args, **kwargs):
    """
    Decorator for printing the function name and location.

    Parameters
    ----------
    *args :
        Positional arguments passed to the decorated function.
    **kwargs :
        Keyword arguments passed to the decorated function.

    Returns
    -------
    func : callable
        A wrapped version of `func` whose output will be printed after executing.

    Examples
    --------
    >>> from pytask import decorator
    >>> @decorator
    ... def my_decorator(func, *args, **kwargs):
    ...     return func()

    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            print(
                f"A function was called named '{func.__name__}' at "
                f"{os.path.abspath(__file__)}:{func.__code__.co_firstlineno}"
            )
            return result

        return inner

    if len(args) > 0:
        return wrapper(args[0])
    elif len(kwargs) > 0:
        return wrapper(**kwargs)
    else:
        raise TypeError("No decorator specified.")


@decorator
def dummy_decorator(func, *args, **kwargs):
    pass


def show_file_path(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        file_name = func.__qualname__
        print(f"The file path is {Path(file_name).resolve()}")
        return result

    return inner


@show_file_path
def dummy_function(filename: str):
    print(f"This is a dummy function that takes one argument: {filename}")


@show_file_path
def another_dummy_function(filename: str):
    print(f"This is another dummy function that takes one argument: {filename}")

# ─── Using decorators in classes ───────────────────────────────────────────────


class Calculator:
    @decorator
    def add(self, x: float, y: float) -> float:
        return x + y

    @decorator
    def multiply(self, x: float, y: float) -> float:
        return x * y


calc = Calculator()
result = calc.add(2, 3)
print(result)

result = calc.multiply(4, 5)
print(result)

# ─── Using decorators in functions ────────────────────────────────────────────
"""Decorators are used to modify or enhance the behavior of functions without changing their source code. They allow you to wrap your functions in additional functionality, such as logging, caching, authentication, etc."""


def calculate(operation: str, x: float, y: float) -> float:
    match operation.lower().strip():
        case "add
@enum.unique
class Status(enum.enum):
    """Statuses of tasks."""

    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


# ─── The class hierarchy for the todo list ───────────────────────────────────

# ─── Task ────────────────────────────────────────────────────────────────────

# ─── Task ────────────────────────────────────────────────────────────────────


# ─── TodoList ────────────────────────────────────────────────────────────────

# ─── Async Context Managers ───────────────────────────────────────────────────

# ─── AsyncContextManager Decorator ────────────────────────────────────────────


async def run_task(task_id: int) -> None:
    print(f"Running task {task_id}...")


async def main():
    # Create a list of tasks with different priorities and statuses
    tasks = [
        Task(id=1, name="Task 1", priority=Priority.NORMAL, status=Status.TODO, tags=["a"]),
        Task(id=2, name="Task 2", priority=Priority.HIGH, status=Status.IN_PROGRESS, tags=["b"]),
        Task(id=3, name="Task 3", priority=Priority.NORMAL, status=Status.DONE, tags=["c"]),
        Task(id=4, name="Task 4", priority=Priority.HIGH, status=Status.TODO, tags=["d"]),
        Task(id=5, name="Task 5", priority=Priority.NORMAL, status=Status.IN_PROGRESS, tags=["e"]),
        Task(id=6, name="Task 6", priority=Priority.HIGH, status=Status.DONE, tags=["f"]),
    ]

    await asyncio.gather(*[run_task(task.id) for task in tasks])


if __name__ == "__main__":
    asyncio.run(main())

# ─── Awaitables, Generators, Coroutines, Tasks ───────────────────────────────

# ─── Async Functions ─────────────────────────────────────────────────────────

# ─── Coroutine Function ───────────────────────────────────────────────────────
"""
A coroutine function is a function that can be paused and resumed during its execution. 
This means it can perform asynchronous operations without blocking the main thread.

To create an asynchronous function, you use the async keyword before the function definition. 
Inside the function body, you can use await expressions to pause the coroutine and wait for other