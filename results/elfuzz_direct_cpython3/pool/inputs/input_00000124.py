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
import sys
import tempfile
import textwrap
import token as tok
import tokenize
import types
import typing
import urllib.parse
import warnings
import weakref
from collections.abc import Mapping, Sequence
from concurrent.futures import Future
from contextlib import (
    AbstractContextManager,
    ContextDecorator,
    suppress,
    redirect_stdout,
)
from dataclasses import InitVar
from datetime import date, datetime
from functools import partial, partialmethod
from io import TextIOWrapper
from itertools import chain, product
from operator import itemgetter
from pathlib import Path
from pprint import pprint
from random import choice, randrange
from re import Pattern
from socket import gaierror
from ssl import SSLError
from signal import SIGTERM
from sys import argv, stderr, stdin, stdout, version_info
from threading import Thread, Lock, Event
from time import sleep, time
from types import ModuleType, TracebackType
from typing import (
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Iterable,
    Iterator,
    Literal,
    NewType,
    NoReturn,
    Optional,
    Protocol,
    Reversible,
    Self,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypedDict,
    Union,
    overload,
)
from typing_extensions import (
    Concatenate,
    ParamSpec,
    TypeGuard,
    Unpack,
    NoTypingInfo,
)

__all__ = [
    "any",
    "counter",  # https://docs.python.org/3/library/threading.html#threading.Event.wait
    "defaultdict_factory",
    "enumerate",
    "get_thread_id",
    "globals_dict",
    "is_instance_of_any",
    "make_counter",
    "NoneOr",
    "no_return",
    "nonempty_iterable",
    "prefixes_and_suffixes",
    "random_password_string",
    "reversed_sequence",
    "timeout_decorator",
    "typed_dict_from_callable",
]

P_ = ParamSpec("P_")

NoneOrT = TypeVar("NoneOrT", None, TypeVar("T"))
"""A union of `None` and any type."""

IterableOfT = TypeVar("IterableOfT")
SeqOfT = TypeVar("SeqOfT")


class HasInit(Protocol[P_]):
    def __init__(self: Self[Unpack[P_]], *args: P_[0], **kwargs