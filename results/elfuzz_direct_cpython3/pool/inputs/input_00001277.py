"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations as TF_PY_3_8_PLUS
import abc
import collections.abc
import functools
import tempfile
import random
import re
import string
import sys
import types
import typing
import warnings
import urllib.request
import zipfile
import concurrent.futures
import tempfile
import contextlib
import http.client
import html.parser
import io
import itertools
import math
import tempfile
import os.path
import struct
import subprocess
import inspect
import pickle
import platform
import queue
import signal
import binascii
import ast
import tokenize
import textwrap
import timeit
from datetime import timedelta
from dataclasses import dataclass
from typing import (
    Any, Callable, ClassVar, Collection, Container, Dict, FrozenSet, Hashable,
    Generic, Iterable, Iterator, List, Mapping, Match, MutableMapping, NamedTuple,
    NewType, Optional, Set, Sequence, Tuple, TypedDict, Union, SupportsInt,
    SupportsFloat, SupportsComplex, SupportsAbs, SupportsBytes, TYPE_CHECKING,
    Type, TypeAlias, TypeGuard, TypeVar, overload, runtime_checkable
)
from typing_extensions import (
    Literal, Final, Protocol, TypedDict, ParamSpec, Concatenate, TypeAlias,
    Never, Annotated, get_args, get_origin, get_origin, get_type_hints,
    reveal_type, NoReturn, Unpack, Self, ForwardRef
)
from collections.abc import AsyncIterator
from itertools import count, dropwhile, islice
from pathlib import Path
from pickletools import dis
from typing import (
    RuntimeWarning, assert_never, get_origin, get_args, get_type_hints,
    reveal_type, assert_never, _eval_type, _eval_node, _format_type,
    _type_repr, _type_repr_with_value
)
import traceback

if sys.version_info >= TF_PY_3_8_PLUS:
    from typing import (
        ClassVar, ForwardRef, ModuleType, TypeAlias, TypeGuard, Unpack, Self
    )
else:
    from typing_extensions import (
        ClassVar, ForwardRef, ModuleType, TypeAlias, TypeGuard, Unpack, Self
    )


def test_str_parser() -> None:
    class Parser:
        def parse(self) -> None:
            ...

    class SimpleParser(Parser):
        """Simple parser."""

        @staticmethod
        def do_stuff() -> None:
            ...

    class MacroParser(Parser):
        """        self.expected_type = expected_type
        self.lo = lo
        self.hi = hi
        self.name: str = "" # TODO: Implement this field.

    def __set_name__(self, owner: type[T], name: str) -> None:
        self.name = name

    def __set__(self, instance: T, value: Any) -> None:
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {self.expected_type}")
        
        if self.lo is not None and value < self.lo or \
           self.hi is not None and value > self.hi:
            raise ValueError(f"{value} out of bounds [{self.lo}, {self.hi}]")
        
        setattr(instance, self.name, value)

    def __get__(self, instance: T, owner: type[T]) -> Any:
        return getattr(instance, self.name)


# ─── INHERITANCE, SUBCLASSES AND SLOTS ───────────────────────────────────────


class BaseClassA(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass: type[BaseClassA]) -> bool: 
        print(f"subclasshook() called with class {subclass.__name__}")
        return NotImplemented
    
    @property
    def val(self):
        return "V1"

class BaseClassB(BaseClassA): pass

print(issubclass(BaseClassB, BaseClassA)) # True


# ──────── 𝗖𝗢𝗥𝗡𝗜𝗧𝗔𝗧𝗜𝗢𝗡 𝘈porto 𝗛𝗲𝗿𝗲 𝗕𝗶𝗻𝗴 𝗠𝗮 𝗰𝗮𝗻 𝗶𝗻𝘁𝗲𝗿𝗽𝗿𝗼𝘀𝘀𝗼𝗿 𝗦𝘂𝗽𝗽𝗼𝗿𝗲𝗱 𝘁𝗵𝗲𝗿𝗲 𝘄𝗶𝗹𝗹 ᴜ𝘀𝗲 𝗼𝗻 𝘆𝗼𝘂𝗿 𝗥𝗲𝘅 tʜ ____h 𝗮𝗻𝗱 𝗳𝘆 𝗩 𝗹𝗲𝗿𝗲.
@functools.total_ordering
class MyNumber(int):
    def __eq__(self, other: int | float) -> bool:
        return super().__eq__(other)
    
    def __lt__(self, other: int | float) -> bool:
        return super().__lt__(other)
    

n1 = MyNumber(42)
assert n1 >= n1 - 1, f"{n1} should be greater than or equal to {n1-1}"
assert n1 <= n1 + 1, f"{n1} should be less than or equal to {n1+1}"

# ─── TYPES, MIRACULOUSLY ─────────────────────────────────────────────────────


def get_class_attributes(cls: type[object]) -> tuple[str]:
    """
    Get all attributes of the given class, including those inherited from its parents.
    """

    attrs = set(dir(cls))
    for parent in cls.mro():
        attrs.update(getattr(parent, "__dict__", {}))

    return tuple(attrs)


class MyClass:

    attr_1 = 1
    attr_2 = "a string"
    attr_3 = [1, 2]

    def method_1(self):
        pass


attrs = get_class_attributes(MyClass)
print(*sorted(attrs), sep="\n")


# ─── METACLASSES ──────────────────────────────────────────────────────────────


class Meta(type):

    def __new__(
        mcs,
        name: str,
        bases: tuple[type],
        namespace: dict[str, Any]
    ) -> type:
        assert "_meta_"