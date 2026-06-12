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
import itertools
import logging
import os.path
import pickle
import secrets
import shutil
import sys
import tempfile
import timeit
import types
import typing
import zipfile
from abc import abstractmethod
from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    Set,
)
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from functools import partial, wraps
from io import StringIO
from multiprocessing.pool import Pool
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from re import compile
from select import select
from signal import SIGINT, SIGTERM
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from struct import pack, unpack
from subprocess import PIPE, STDOUT, Popen, check_call, check_output
from threading import Thread
from time import sleep
from tokenize import NAME
from traceback import format_exception_only
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    ClassVar,
    Coroutine,
    Dict,
    Generic,
    List,
    Literal,
    NoReturn,
    Optional,
    Pattern,
    Tuple,
    TypeVar,
    Union,
)
from unittest.mock import Mock
from weakref import proxy


class ClassProperty:
    """Class property decorator.

    Example:

        >>> class C:
        ...     _x = 'foo'
        ...
        ...     @classmethod
        ...     def x(cls):
        ...         return cls._x
        ...
        ...     @x.setter
        ...     def x(self, value):
        ...         self._x = value
        ...
        ...     @x.deleter
        ...     def x(self):
        ...         del self._x
        ...

    Source:
    https://stackoverflow.com/a/21938703/355230
    """

    def __init__(self, fget=None):
        if not callable(fget):
            raise TypeError('a descriptor must be a callable')
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)

    def getter(self, fget):
        new_prop = type(self)(fget=fget)
        new_prop.__doc__ = getattr(self, '__doc__', None)
        return new_prop

    def setter(self, f