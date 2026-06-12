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


logger = getLogger(__name__)


##########################################################################
# ThreadLocks: functions to prevent race conditions and deadlocks.
##########################################################################

def lock(func: Callable[..., None]) -> Callable[..., None]:
	"""Decorator for locking a function.

	Thread-safe.
	"""

	def wrapper(*args: object, **kwargs: object) -> None:
		with thread_lock():
			return func(*args, **kwargs)

	wraps(func)(wrapper)


def thread_lock() -> threading.Lock:
	"""Thread-local lock."""
	if not hasattr(threading.local(), "lock"):
		threading.local().lock = threading.Lock()
	return getattr(threading.local(), "lock")


@overload
def multi_threaded(f