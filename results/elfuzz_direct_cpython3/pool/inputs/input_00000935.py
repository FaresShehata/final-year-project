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
import tempfile
import textwrap
import threading
import time
import re
import sys
import types
import typing
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field, fields, InitVar, make_dataclass
from decimal import Decimal
from enum import Enum, auto, unique
from fractions import Fraction
from functools import partial, wraps
from inspect import Attribute, Parameter, signature
from itertools import chain
from keyword import iskeyword
from math import log
from operator import attrgetter, itemgetter
from pathlib import Path
from pprint import PrettyPrinter
from pyrsistent import PClass, field, pmapfield, pvectorfield, persistent
from typing import (
	Any, AnyStr, Callable, ClassVar, Dict, Generic, Hashable, IO, Iterable,
	List, Literal, Mapping, Match, NoReturn, Optional, Pattern, Sequence,
	Set, SupportsIndex, Tuple, Type, TypedDict, Union, get_args, get_origin,
	get_type_hints, overload, runtime_checkable, TypeGuard, TypeVar,
	TypeVarTuple, VarArg, VarKwArg, _SpecialForm, _T_co, _T_contra,
	_AnyTypeVars, _InferGenericArgs, _Protocol
)
from weakref import ref
import tokenize
#from textwrap import dedent
from typing_extensions import TYPE_CHECKING, ClassVar, Self, TypeAlias
from typing_inspect import is_typeddict_v2, is_union_type, get_args as ti_get_args
import contextlib
import csv
import datetime
import filecmp
import fnmatch
import fcntl
import functools
import heapq
import importlib.util
import ipaddress
import itertools
import json
import keyword
import linecache
import locale
import logging
import lzma
import mmap
import mimetypes
import multiprocessing
import os
import platform
import random
import reprlib
import signal
import shutil
import socket
import sqlite3
import subprocess
import sysconfig
import tarfile
import tempfile
import textwrap
import threading
import time
import token
import tokenize
import tokenize2
import traceback
import types
import uuid
import warnings
import zipfile

import concurrent.futures
import contextlib
import contextvars
import copyreg
import doctest
import email.message
import errno
import html.parser
import http.client
import http.cookiejar
import http.server
import http.cookies
import httplib	/**
	 * Whether or not the person is a student.
	 */
	is_student: bool
"""

JsArray: TypeAlias = List[JsObject]

js_obj_str: JsonStr = """[
    {
        "name": "John",
        "age": 30,
        "city": "New York"
    },
    {
        "name": "Jane",
        "age": 28,
        "city": "London"
    }
]"""

# type aliases for JSON object and array

JsonObj: TypeAlias = Dict[str, Any]
JsonArr: TypeAlias = List[Any]


def main() -> None:
	print("seed 05")


if __name__ == "__main__":
	main()

"""
Seed 05 - Advanced typing features available in Python 3.10+
"""


class Point(metaclass=ABCMeta):
	x: int | float
	y: int | float


@dataclass(slots=True)
class Line(Point):
	length: float


print(Point.__mro__)


def add(a: str, b: str) -> str:
	return a + b


print(add("hello", "world"))

print(add(1, 2))

# this will fail because one of the arguments is not a string
# print(add(1, 2))


def add_any(*args: Any) -> Any:
	return sum(args)


print(add_any(1, 2))
print(add_any([1], [2]))
print(add_any([1], {2}))
print(add_any([1], {"a": 2}))
print(add_any((1,), (2,)))
print(add_any({1}, {2}))


def div(a: float, b: float) -> float:
	return a / b


print(div(1, 2))
print(div(1.0, 2))
print(div(1, 2.0))


def is_prime(n: int) -> bool:
	if n < 2:
		return False
	for i in range(2, int(n ** 0.5) + 1):
		if n % i == 0:
			return False
	return True


print(is_prime(7))
print(is_prime(9))


def is_even(num: int) -> bool:
	return num % 2 == 0


print(is_even(4))
print(is_even(7))


def is_odd(num: int) -> bool:
	return num % 2 != 0


print(is_odd(4))
print(is_odd(7))


def is_multiple_of_5_and_3(num: int) -> bool:
	return num % 5 == 0 and num % 3 == 0


print(is_multiple_of_5_and_3(15))
print(is_multiple_of_5_and_3(18))


def is_multiple_of_5_or_3(num: int) -> bool:
	return num % 5 == 0 or num % 3 == 0


print(is_multiple_of_5_or_3(15))
print(is_multiple_of_5_or_3(18))


def is_divisible_by(num: