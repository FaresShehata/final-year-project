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
import json
import multiprocessing
import os
import os.path as osp
import random
import re
import secrets
from collections.abc import Iterator, Iterable, Hashable
from dataclasses import InitVar, dataclass, field, fields, fields_dict
from enum import Enum
from functools import partialmethod
from itertools import chain, accumulate
from operator import itemgetter
from pathlib import Path
import platform
import re
import sys
import tempfile
import threading
import tokenize
import textwrap
from typing import (
    Any,
    Callable,
    ClassVar,
    Literal,
    NoReturn,
    NewType,
    Optional,
    Protocol,
    TypedDict, 
    Union,
)
import warnings
from weakref import WeakSet, ref, WeakKeyDictionary


# Seed 02 — Duck Typing, Type Hints, Unpacking, *args, **kwargs,
#           type(), isinstance(), issubclass(),
#           @staticmethod, @classmethod, with self in parameter list


def seed_2_duck_typing() -> None:

    class A(object):
        pass

    # two ways of referencing a function or method
    def f(a: str = 'hello') -> str:
        return f'Hello {a}!'
    
    g = f

    print(g.__name__) # <function f at ...>

    print(g) # <function f at ...>
    

    # print(f(1))

    # lambda functions are also objects that can have attributes.
    f = lambda x: True
    f.x = 10

    print(hasattr(f, 'x')) # True
    

def seed_3_type_hints() -> None:

    FooBarbaz = NewType('FooBarBaz', dict)

    foo_bar_baz = FooBarbaz({'foo': 1, 'bar': 2})

    print(foo_bar_baz['foo']) # 1
    
    print(type(foo_bar_baz)) # <NewType 'FooBarBaz'>



def seed_4_unpacking() -> None:

    l = [1, 2, 3]

    # packing
    p = *[l[0], l[1]]

    # unpacking
    print(*p)


def seed_5_args_kwargs() -> None:

    def f(x=None, y=1):

        print(x, y)
        
    args = {'y': 2}
    kwargs = {'x': 1
def seed_11_exception_handling() -> None:
    """Exception handling and assertions"""

    def divide(num1: int, num2: int) -> int:
        if num2 == 0:
            raise ZeroDivisionError('num2 cannot be zero')
        else:
            return num1 // num2