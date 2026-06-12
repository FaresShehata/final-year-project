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
from pprint import pformat, pprint
from queue import Queue, SimpleQueue
from random import shuffle, uniform
from reprlib import RecursiveRepr, repr
from resource import getrusage, RUSAGE_SELF
from statistics import median, mean
from string import Formatter
from types import FrameType, TracebackType
from typing import (
    Any,
    Callable,
    Collection,
    ContextManager,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Pattern,
    Set,
    Tuple,
    Union,
)
from urllib.request import urlretrieve
from weakref import ReferenceType, WeakKeyDictionary, WeakSet

from _pytest.monkeypatch import MonkeyPatch


class Mock(MonkeyPatch):

    def __init__(self, module: str | list[str], attr: str, value: Any = None) -> None:
        if isinstance(module, list):
            modules = module
            names = [attr]
        else:
            modules = [module]
            names = [attr]

        super().__init__(*modules, names)
        self.value = value

    def __enter__(self):
        for mod in self.modules:
            setattr(mod, self.names[0], self.value or type(self.value)(getattr(mod, self.names[0])))



""" 
Miscellaneous modules:

- argparse, argparse.ArgumentParser, argparse.Action, argparse.ArgumentError,
  argparse.HelpFormatter, argparse.SUPPRESS, ArgumentTypeError, util
- atexit, signal, heapq, bisect, bisect_left, bisect_right, sortedlist,
  sortedcontainers
- doctest, unittest, unittest.TestCase, unittest.TestResult, unittest.TestSuite,
  unittest.TextTestRunner, unittest.defaultTestLoader, unittest.skipIf,
  unittest.suite, unittest.case, unittest.loader, unittest.skipUnless,
  unittest.runner, unittest.result, unittest.main, unittest.findTestCases,
  unittest.IsolatedAsyncioTestCase, unittest.isort
- enum, Enum, IntEnum, Flag, auto, unique, IntFlag, IntMeta, IntDescr,
  EnumMeta, _generate_next_value_, EnumMember, EnumException, EnumRegister,
  EnumClass
- functools, partial, partialmethod, lru_cache, singledispatch, wraps, update_wrapper,
  reduce, cmp_to_key, itemgetter, methodcaller, cacheit, partialmethod, cached_property,
  cached_method, cached_classmethod, lru_cache, lru_cache_factory
- html, html.escape, html.unescape, html.parser.HTMLParser, escape, unescape,
  parse, escape_uri_component, unescape_uri_component, Markup, unescape_markup
- hashlib, sha1, sha256, sha512, md5, sha384, blake2b, blake2s, pbkdf2_hmac, hash_info,
  hashes, algorithms, util
- json, JSONDecodeError, loads, load, dumps, dump, encoder, decoder, scanner, scanstring,
  decoder.JSONDecoder, encoder.Encoder, default, indentless, separators, cls
- ipaddress, IPv4Address, IPv6Address, IPv4Network, IPv6Network          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
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
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    return new_fn

def patch_code_object(code: bytes, *, **kwargs) -> bytes:
    """
    Patch the contents of an existing code object and return it.
    
    This works by converting to/from a bytearray (which is mutable), then back
    into bytes.
    
    Keyword arguments are passed on to `dis.Bytecode`.
    """

    bco = bytearray(code)
    dis.Bytecode(bco).patch(**kwargs)
    return bytes(bco)


# ── Ctypes & struct ───────────────────────────────────────────────────────────

class BuiltinFunc(object):

    def __init__(self, func):
        self._func = func
        self._arg_names = None

    @property
    def arg_names(self):
        if self._arg_names is None:
            self._arg_names = [a.argval for a in self.func.func_code.co_varnames]
        return self._arg_names

def struct_unpack(ty, s):
    if ty[0] not in 'bhilq':
        raise ValueError('unsupported format character')
    fmt = f'<{ty}' if sys.byteorder == 'little' else f'>{ty}'
    size = struct.calcsize(fmt)
    if len(s) < size:
        raise ValueError(f'string too short ({len(s)} vs {size})')
    n = struct.unpack(fmt, s[:size])[0]
    return n, s[size:]

def cdef_struct(name, fields=None, packed=False):
    if isinstance(fields, str):
        name, fields = fields.split(':', maxsplit=1)

    class S(Structure):
        _fields_ = [(name, field_type)]
        if packed:
            _pack_ = 1

    return S

cdef_struct('mystruct', ('x', 'h'), packed=True)
B = cdef_struct('A', ('b', 'd'))
C = cdef_struct('B', ('e', 'f'))

class A(B, C):

    def __init__(self, x, y, z):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z

class B(C, A):

    def __init__(self, w, z):
        super().__init__()
        self.w = w
        self.z = z

print(A.z.__getattribute__)
print(A.__dict__)

# ── Array & Memoryview ────────────────────────────────────────────────────────

