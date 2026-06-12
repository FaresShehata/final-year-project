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
import os
import re
import secrets
import shutil
import sys
import tempfile
import threading
import tokenize
import types
import time
import traceback
import urllib.parse as urlparse
import uuid
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import Iterable, Iterator, Sequence, Callable
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import partial, wraps, lru_cache, singledispatchmethod
from inspect import signature, Parameter, isawaitable, AsyncGenerator, iscoroutinefunction
from io import TextIOWrapper
from itertools import chain
from logging import getLogger, CRITICAL, WARNING, ERROR
from operator import itemgetter
from pprint import pformat
from random import choice, randint
from re import Pattern
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from typing import (
    Any,
    overload,
    Awaitable,
    NoReturn,
    Optional,
    Union,
    Tuple,
    List,
    Dict,
    Generator,
    Deque,
    Set,
    FrozenSet,
    ClassVar,
    Mapping,
    Counter,
    Generic,
    Protocol,
)
from typing_extensions import Literal, TypedDict, ParamSpec, Concatenate, TypeAlias, Never, Annotated, get_args, get_origin, _AnnotatedAlias
from types import CodeType, FunctionType, BuiltinFunctionType, MethodType, ModuleType
from weakref import WeakValueDictionary, ref
from zlib import crc32

from .base import BaseObject, ObjectMap, ObjectArray, ObjectSeq, ObjectTuple, ObjectSet, ObjectFrozenSet, ObjectEnum, ObjectList, ObjectDeque, ObjectCounter, ValueTypes
from ..utils.misc import *
from ..utils.collection import Queue
from ...core.utils.logger import Logger
from ...core.utils.type_utils import *


__all__ = [
    "BaseString", "StringTypes", "Text",
    "AnyStr", "ByteString", "Bytes", "ByteArray", "BinaryIO",
    "fstr", "t_str", "as_bytes", "s_bytes", "b_str",
    "parse_tuple_str", "parse_list_str", "parse_dict_str", "parse_set_str", "parse_frozen_set_str", "parse_enum_str", "parse_seq_str",
    "get_string_repr",
    "seed_threading", "seed_multiprocessing", "seed_concurrent_futures",
    "seed_string_parsing",
    "seed_typing_extras",
    "seed_class_member_decorators",
    "seed_contextlib",
    "seed_numbers_abc",
    "seed_pathlib",
    "seed_tempfile",
    "seed_csv",
    "seed_base64",
    "seed_hashlib",
    "seed_hmac",
    "seed_secrets",
]


def seed_threading():
    """
    Seeds the global ``random`` module for ``Thread`` and ``Lock``.

    :return: None.
    """

    from ..seed.core.seed_random import seed_random_module

    # Seed the global 'random' module to avoid thread locking issues when running in parallel.
    seed_random_module()


def seed_multiprocessing():
    """
    Seeds the global ``Random`` module for ``Process`` using the current process ID.

    :return: None.
    """

    from ..seed.core.seed_random import seed_random_module

    try:
        from multiprocessing import current_process, RandomState
    except ImportError:
        return

    pid = getattr(current_process(), "_identity", [None])[0]

    if pid is not None:
        seed_random_module(RandomState(pid))


def seed_concurrent_futures():
    """
    Seeds the global ``ThreadPoolExecutor`` with a pool of fixed-size threads by default.

    :return: None.
    """

    from concurrent.futures import ThreadPoolExecutor

    # Make sure we have at least one worker thread available or else the global
    # `ThreadPoolExecutor` will use all CPU cores on your machine which can lead to
    # performance issues and unresponsive code execution.
    num_workers = max(1, int(os.cpu_count() / 2))

    executor = ThreadPoolExecutor(max_workers=num_workers)
    setattr(ThreadPoolExecutor, "__orig_init__", ThreadPoolExecutor.__init__)
    ThreadPoolExecutor.__init__ = lambda self, *args, **kwargs: ThreadPoolExecutor.__orig_init__(self, *args, **{**kwargs, "max_workers": min(num_workers, kwargs.get("max_workers", 1))})


def seed_string_parsing():
    """
    Seeds the standard library's ``ast``, ``tokenize``, ``textwrap``,
    ``string.Formatter``, ``typing.Extra`` modules.

    :return: None.
    """

    from ..seed.string_parser import *

    import ast
    import tokenize
    import textwrap
    import string
    import typing

    # Seeding the standard library's `ast`, `tokenize`, `text