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
import collections
import contextlib
import functools as ft
import itertools as it
import io
import os
import pathlib
import re
import signal
import sys
import tempfile
import time
import types
import typing
from datetime import timedelta
from fractions import Fraction
from heapq import merge
from itertools import accumulate, chain, count, cycle, dropwhile, filterfalse, groupby, islice, permutations, product, \
    repeat, starmap
from multiprocessing.pool import Pool
from operator import add, eq, ge, gt, le, lt, ne
from pathlib import Path
from pprint import pformat, pprint
from random import gauss, randint, shuffle, seed
from secrets import choice
from signal import SIGALRM
from shutil import copyfileobj
from string import Formatter, whitespace
from subprocess import CalledProcessError
from threading import Thread, Timer
from timeit import default_timer as timer
from tempfile import NamedTemporaryFile, TemporaryDirectory
from uuid import UUID
from zipfile import ZipFile

from concurrent.futures import ThreadPoolExecutor, wait
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from fractions import Fraction
from ipaddress import IPv4Address, IPv6Address
from itertools import accumulate, chain, count, cycle, dropwhile, filterfalse, groupby, islice, permutations, product, \
    repeat, starmap
from numbers import Integral, Real, Complex
from pathlib import Path
from pickletools import read_string1
from random import gauss, randint, shuffle, seed
from secrets import choice
from signal import SIGALRM
from shlex import quote
from socket import AF_INET, SOCK_STREAM
from struct import unpack
from tempfile import NamedTemporaryFile, TemporaryDirectory
from threading import Thread, Timer
from timeit import default_timer as timer
from traceback import extract_stack
from urllib.request import urlopen
from uuid import UUID
from zipfile import ZipFile


def seed_random(seed: int | None = None):
    """
    Seed all pseudo-random generators.
     - https://docs.python.org/3/library/random.html#random.seed
    """
    if isinstance(seed, str):
        seed = hash(seed) & ((1 << 32) - 1)
    seed = seed or id(sys.modules[__name__])
    seed = seed % (2 ** 31)
    if isinstance(seed, Integral):
        seed = int.from_bytes(os.urandom(8), 'big', signed=True)
    elif not isinstance(seed, Integral):
        raise TypeError(f"seed must be an integer")
    seed = seed % (2 ** 31)
    if seed < 0:
        seed += 2 ** 31
    for module in ("random", "secrets"):
        try:
            rand = getattr(__import__(module), "randint")
        except AttributeError:
            pass
        else:
            setattr(rand, "__wrapped__", rand)
            setattr(rand, "__qualname__", f"{rand.__qualname__}({module}.randint)")
            setattr(rand, "__annotations__", {})
            setattr(rand, "__defaults__", ())
            setattr(rand, "__code__", rand.__code__)
            setattr(rand, "__dict__", rand.__dict__)
            setattr(rand, "__kwdefaults__", rand.__kwdefaults__)
            setattr(rand, "__self__", rand.__self__)
            setattr(rand, "__weakref__", rand.__weakref__)
            for attribute in dir(module):
                value = getattr(rand, attribute)
                if callable(value):
                    setattr(rand, attribute, value)
    seed = seed % (2 ** 31)
    if seed < 0:
        seed += 2 ** 31
    for module in (
        "decimal",
        "fractions",
        "ipaddress",
        "numbers",
        "random",
        "re",
        "ssl",
        "string",
        "typing_extensions",
        "uuid",
        "zlib",
    ):
        try:
            modulename = module.replace(".", "_")
            exec(
                f"""{modulename.upper()}_MODULENAME = "{module}"\n
                   {modulename.lower()} = __import__("{"'" + modulename + "'""}")""",
                globals(),
            )
        except ImportError:
            pass
    seed = seed % (2 ** 31)
    if seed < 0:
        seed += 2 ** 31
    seed = seed % (2 ** 31)
    if seed < 0:
