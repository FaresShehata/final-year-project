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
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NewType,
    NoReturn,
    Optional,
    ParamSpec,
    Protocol,
    Self,
    Sequence,
    Tuple,
    TypedDict,
    TypeGuard,
    Union,
    ValuesView,
    GetAttrProtocol,
    SupportsIndex,
    SupportsComplex,
    SupportsFloat,
    SupportsInt,
    SupportsRound,
    overload,
    runtime_checkable,
)
import sys
import types
import typeshed
import unittest.mock
import weakref
from abc import abstractmethod
from collections.abc import Coroutine, Iterable, Mapping, MutableMapping
from dataclasses import dataclass
from enum import Enum
from functools import partial
from heapq import heapify, nlargest, nsmallest
from inspect import signature
from itertools import chain, starmap
from operator import indexOf, is_
from pathlib import Path
from random import Random
from re import compile
from shlex import split
from signal import Signals
from statistics import median, pvariance
from string import Formatter
from subprocess import PIPE, Popen, STDOUT
from typing_extensions import (
    Concatenate,
    ParamSpecArgs,
    GetAttrKwargs,
    SelfKWArgs,
)
from warnings import warn


# list comprehensions --------------------------------------------------------------

x = [i + 1 if i < 5 else -i for i in range(10)] 
y = [(x ** 2 + y ** 2) / 2 for x, y in zip(range(10), range(10))]
z = [[x for x in range(10)] for _ in range(10)]

a = [
    i**2 if i % 2 == 0 else -i 
    for i in range(10) 
]

b = [
    i**2 if i % 2 == 0 else -i
    for i in range(10) 
]


c = []
for i in range(10): 
    if i % 2 == 0: c.append(i**2) 
    else: c.append(-i)


d = [
    i**2 if i % 2 == 0 else -i
    for i in range(10) 
    if i % 2 == 0 
]


e = {
    'foo': 'bar',
    'baz': 10,
}


f = {k.upper(): v for k, v in e.items()}

g = {}

for key, value in    
    @property
    def value(self):
        return self.key * 2
    
    
def protocols_example():
    items = [Item(i) for i in range(10)]
    
    count_by_key = {}
    for item in items:
        count_by_key.setdefault(item.value, 0)
        count_by_key[item.value] += 1
        
        
    # generic protocol with type variable
    T = TypeVar('T')
    class SupportsMagicMethod(Generic[T], Protocol):
        def __magic_method__(self, other: T) -> bool: ... 
        
        @classmethod
        def __subclasshook__(cls, subclass: type) -> bool: ...
        
        
    def do_magic_method(item_1: SupportsMagicMethod[int], item_2: SupportsMagicMethod[int]) -> bool:
        return item_1.__magic_method__(item_2)
        
    
# data classes ---------------------------------------------------------------

class Person(dataclasses.dataclass):
    name: str
    age: int
    phone_numbers: List[str]
    email: Optional[str] = None 


def example_data_classes():
    person = Person('John Doe', 30, ['+1-867-5309'], email='john.doe@example.com')