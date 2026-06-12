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
import timeit
import types
import typing
import typing_extensions as te
import urllib.parse
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import (
    MutableMapping,
    Sequence,
)
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from itertools import chain, cycle, tee
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import sample
from re import Pattern
from sys import argv
from types import CodeType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
)
from uuid import UUID
from typing_extensions import (
    Self,
    Unpack,
    assert_never,
    Annotated,
    ParamSpec,
    Concatenate,
    TypeGuard,
)
from urllib.parse import urlparse

import csvkit
import numpy as np
from IPython.display import display, Markdown, clear_output
from IPython.utils.io import capture_output, capture_stdin
from ipywidgets.widgets import Dropdown, Button, Layout
from pathtools.path import PathLike
from pydantic import BaseModel, Field, parse_obj_as, validator
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import track
from rich.text import Text
from rich.align import Align
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.panel import Panel
from rich.padding import Padding
from rich.syntax import Syntax
from rich.tree import Tree
from rich.style import Style
from rich.console import ConsoleRenderable
from rich.repr import RichReprResult
from rich.traceback import Traceback


console = Console()
highlighter = ReprHighlighter()
T = TypeVar("T")
U = TypeVar("U")


# ================================================================
# Seed 01: Basic data structures and iteration
# ================================================================

def basic_data_structures_and_iteration():
    """
    ## Basic data structures and iteration

    ### Questions:

    - What is the difference between a list and an array?
    - How can you iterate over elements in a set?
    - Why is it important to use `break` or `return` in loops?

    ### Answers:

    - A list is mutable, while an array is immutable.
    - You can iterate over elements in a set using the `for...in` loop.
    - It's important to use `break` or `return` in loops to exit early if the result of evaluating an expression has already been determined.

    """

    # Lists are mutable:
    l = [1, 2, "three", True]
    l.append(4)
    print(l)

    # Arrays are immutable:
    arr = np.array([1, 2, "three", True])
    arr[3] = False
    print(arr)

    # Sets are iterable but not indexable:
    s = {1, 2, "three", True}
    for el in s:
        print(el)


# ================================================================
# Seed 02: String formatting with str.format
# ================================================================

def format_string():
    """## Format strings

    ### Question:

    - What will this program output?

    ```python
    name = input('What is your name? ')
    print('Hello {}!'.format(name))
    ```

    ### Answer:

    The result of running this program would be something like:

    ```
    Hello John!
    ```

    where `John` was entered by the user at runtime.

    """
    name = input("What is your name?")
    print(f"Hello {name}!")


# ================================================================
# Seed 03: String formatting with f-strings
