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
    "seed_class_decorators",
    "seed_contextlib",
    "seed_numbers_abc",
    "seed_pathlib",
    "seed_tempfile",
    "seed_csv", "seed_base64", "seed_hashlib", "seed_hmac", "seed_secrets",
]

logger = getLogger(__name__)
if not logger.isEnabledFor(CRITICAL):
    logger.setLevel(WARNING)


# noinspection PyUnresolvedReferences
def seed_seed():
    """Randomly set the seeds of all modules that have a seed() function."""
    # noinspection PyProtectedMember
    from ..core.seeders.base import Seeders


class BaseString(str, Generic[Self], metaclass=ABCMeta):
    @abstractmethod
    def fstr(self) -> str: return NotImplemented
    @classmethod
    @abstractmethod
    def parse(cls, s: str | Self) -> Self: return NotImplemented
    @staticmethod
    @abstractmethod
    def is_valid(s: str) -> bool: return NotImplemented

    @overload
    @classmethod
    def parse_many(cls, *args: str | Self) -> list[Self]: ...
    @overload
    @classmethod
    def parse_many(cls, iterable: Iterable[str | Self]) -> list[Self]: ...

    @classmethod
    def parse_many(cls, *args: str | Self) -> list[Self]:
        return [cls.parse(x) for x in args]

    @classmethod
    def bytes(cls, string: str | bytes | bytearray, encoding: str = "utf-8") -> bytes:
        if isinstance(string, str):
            return cls.encode(string, encoding)
        elif isinstance(string, (bytes, bytearray)):
            return string
        else:
           