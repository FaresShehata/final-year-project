"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining
"""

from __future__ import annotations

import functools
import itertools
import operator
import sys
from collections.abc import Callable, Generator, Iterable, Iterator
from typing import Any, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# ── Lambda-calculus church encodings ─────────────────────────────────────────

TRUE  = lambda t: lambda f: t
FALSE = lambda t: lambda f: f
IF    = lambda b: lambda t: lambda f: b(t)(f)
AND   = lambda p: lambda q: p(q)(p)
OR    = lambda p: lambda q: p(p)(q)
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)
PRED  = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g))(lambda y: x(y))

# ──────── End of encoding ───────────────────────────────────────────────────

def is_even(x: int) -> bool:
    return NOT(AND(x % TWO == ONE, x % THREE == ONE))()

# ───────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    print(is_even(2),     # True
          is_even(17),    # False
          is_even(-5),    # False
          sep="\n")


"""This module represents the following tasks:

- task 03.01 - create a function is_odd that returns True if its argument is odd and False otherwise.
              Use lambdas, not built-in operators like % or ==
- task 03.02 - create a function is_prime that checks whether an integer value is prime using the is_odd function.
              Do it with lambdas only.

❗️ Note that this exercise requires some knowledge of types. You will need to use
type hints for all arguments and return values in your solutions. Also remember
that type annotations are just hints for static type checkers.

To make sure you have understood the requirements correctly, run the script
with the --test option.

If you want to learn more about Python’s builtin type system, please refer to
the documentation at https://docs.python.org/3/library/typing.html

Python also supports optional type annotations which can be used to provide
information about the expected type of arguments and return values.
You can find out how to work with them here:
https://www.python.org/dev/peps/pep-0484/

While writing your code, you may also want to consider other features introduced
in Python versions earlier than 3.9 such as metaclasses, decorators, generics,
context managers etc. Please note however that these features are not available
on older Python interpreters so they should be avoided when writing scripts
which will be portable across different platforms.

Modules provided by default on most systems include:

          abc, argparse, array, asyncio, bisect, bz2, cProfile, calendar, colorsys,
          configparser, contextvars, copyreg, curses, datetime, difflib, email,
          enum, fractions, getopt, gzip, html, http.cookies, http.client, ipaddress,
<|fim_pad|><|fim_pad|>          __class_getitem__, __set_name__, __init_subclass__,
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
