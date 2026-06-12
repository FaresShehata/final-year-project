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
import functools
import io
import io.abc
import itertools
import json
import logging
import os
import pickle
import pickletools
import secrets
import signal
import sys
import threading
import timeit
import this as tthis_is_the_thing_with_a_y
import tokenize
import types
import typing
import urllib.request
import urllib.error
import zlib
from collections import deque, Counter, defaultdict
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum, auto
from fractions import Fraction
from gc import collect
from hashlib import sha1
from html.parser import HTMLParser
from io import StringIO, TextIOBase, TextIOWrapper
from itertools import chain, zip_longest
from math import ceil, cos, radians
from multiprocessing.context import Process
from multiprocessing.pool import Pool
from operator import attrgetter, itemgetter
from os.path import dirname, realpath, join, basename
from pathlib import Path
from pprint import pformat
from queue import Queue, Empty
from re import Pattern, compile, match, subn
from reprlib import recursive_repr
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE, SelectorKey
from statistics import mean, median, pstdev, StatisticsError
from string import Formatter, Template, TemplateMatch, ascii_letters, digits
from typing import (
    Any, Callable, ClassVar, Container, Coroutine, Dict, FrozenSet, Generic,
    Hashable, Iterable, Iterator, List, Mapping, Match, MutableMapping, Optional,
    Sequence, Set, Tuple, Type, TypeVar, Union, cast, overload, runtime_checkable,
)
from typing_extensions import Literal, Protocol, TypedDict, ParamSpec, Concatenate
from warnings import warn, catch_warnings

# ---

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
W = TypeVar('W')

S = TypeVar('S', bound='StrType')

P = ParamSpec('P')
R = TypeVar('R')


def _decorator_noargs(func: Callable[P, R]) -> Callable[..., R]:
    @functools.wraps(func) # type: ignore[arg-type]
    def wrapper(*_, **__) -> R:
        return func()
    
    return wrapper


class Coder(Protocol):
    
    def encode(self, s: str) -> bytes:
        ...

    def decode(self, b: bytes) -> str:
        ...


class Encoder(Coder):
    pass


class Decoder(Coder):
    pass


class Codec(Adapter[Encoder, Decoder]):
    ...
    

@overload
def decode(s: None, c: Encoder | Decoder) -> None:
    ...


@overload
def decode(s: str, c: Encoder | Decoder) -> bytes:
    ...


def decode(s: Optional[str], c: Encoder | Decoder) -> Union[bytes, None]:
    if s is not None:
        return c.decode(s)


@overload
def encode(b: bytes, c: Encoder | Decoder) -> str:
    ...


@overload
def encode(b: None, c: Encoder | Decoder) -> None:
    ...


def encode(b: Optional[bytes], c: Encoder | Decoder) -> Union[str, None]:
    if b is not None:
        return c.encode(b)

        
class StrType(str, Protocol[S]):
    ...


class MyStr(StrType['MyStr']):
    ...


class MyDecoder(Decoder):
    def decode(self, b: bytes) -> str:
        return b.decode('utf-8') + ' foo'


class MyCoder(Coder):
    def encode(self, s: str) -> bytes:
        return s.encode('utf-8') + b' bar'

        
def f(c: Coder) -> None:
    print(decode(c.encode('hello'), c))
    print(encode('world'.encode('latin1'), c).decode())
    
    
f(MyCoder())

x: Coder = MyCoder()

print(x.encode('foo'))

f(x)

x = MyCoder()

r = x.encode('bar')

type(r) # type: ignore[arg-type]

y: bytes = r
    
print(y.decode())

z: str = y.decode().upper()


class C2(Coder):
    def encode(self, s: str) -> bytes:
        return super().encode(s[::-1