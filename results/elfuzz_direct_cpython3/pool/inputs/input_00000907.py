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


class StrType(str):
    pass


@overload
def append(x: list[T], y: T) -> None:
    ...


@overload
def append(x: list[S], y: S) -> S:
    ...


def append(x: list[U] | str, y: U) -> list[U] | str:
    x.append(y)
    return x if