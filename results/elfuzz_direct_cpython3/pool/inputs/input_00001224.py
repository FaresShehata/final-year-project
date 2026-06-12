"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
from collections import Counter, defaultdict, deque
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Literal,
    Protocol,
    Sequence,
    Tuple,
    TypeAlias,
    Union,
)

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import ParamSpec
else:
    class P: pass
    P = P()

# TODO: Add a link to the official docs about "async all" and "async any"

class AsyncEnum(enum.Enum):
    """An abstract base class for asynchronous enumerations."""

    @classmethod
    def _generate_next_value_(
        cls: type[AsyncEnum],
        value: str | int,
        start: int | None = None,
        count: int | None = None,
        last_values: list[str] | None = None,
    ) -> str:
        return value


@dataclasses.dataclass(frozen=True)
class DataClassA:
    x: int
    y: int
    z: float

    class XError(Exception):
        ...

    @property
    def x(self) -> int | AsyncEnum.XError:
        try:
            if self._x < 0:
                raise self.XError("X is less than zero.")
            if self._x > 100:
                raise self.XError("X is greater than one hundred.")
            return self._x
        except AttributeError:
            raise self.XError("X property has not been initialized.")

    @x.setter
    def x(self, value: int) -> None:
        self._x = value

    class YError(Exception):
        ...

    @property
    def y(self) -> int | AsyncEnum.YError:
        try:
            if self._y < 0:
                raise self.YError("Y is less than zero.")
            if self._y > 100:
                raise self.YError("Y is greater than one hundred.")
            return self._y
        except AttributeError:
            raise self.YError("Y property has not been initialized.")

    @y.setter
    def y(self, value: int) -> None:
        self._y = value

    class ZError(Exception):
        ...

    @property
    def z(self) -> float | AsyncEnum.ZError:
        try:
            if self._z < 0:
                raise self.ZError("Z is less than zero.")
            if self._z > 1e+100:
                raise self.ZError("Z is greater than one billion.")
            return self._z
        except AttributeError:
            raise self.ZError("Z property has not been initialized.")

    @z.setter
    def z(self, value: float) -> None:
        self._z = value

    def __post_init__(self) -> None:
        self.x += 1
        self.y -= 1
        self.z *= 2

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.x}, {self.y}, {self.z})"


DataClassB = dataclasses.make_dataclass(
    'DataClassB',
    [
        ('x', int),
        ('y', int),
        ('z', float),
    ],
)


print(DataClassA.__annotations__)
print(DataClassA.__dict__)

print(DataClassB.__annotations__)
print(DataClassB.__dict__)


class ImmutableDataClassA(dataclasses.dataclass(frozen    lambda x, y: x * y,
    (z := lambda z: z**3)(5),
]


for fn in funcs:
    cobj = compile(fn, "<string>", "exec")

    print("\nFunction source:")
    print(cobj.co_code)
    print()

    print("\nFunction bytecode:")
    print(list(dis.get_instructions(cobj)))

    print("\nFunction globals:")
    print(inspect.getmembers(cobj.globals))

    print("\nFunction locals:")
    print(inspect.getmembers(cobj.locals))


# ── Executing a bytecode sequence ──────────────────────────────────────────────
#
# Note: The original function must be defined at the point where it's called.
#

def exec_bytecode(code: bytes, env: dict[str, Any]) -> None:
    """
    Execute a list of bytecode instructions.

    >>> env = {'a': 3}
    >>> exec_bytecode(b"\x7f\xef\xff\xd8", env)  # "\x7f\xef\xff\xd8" == b"\x7fELF"
    >>> env['a']
    3
    """
    assert isinstance(env, dict)
    locs = env.copy()
    for op, arg in dis.findlinestarts(code):
        if op.startswith("LOAD_"):
            key = op[5:].lower().replace("_", "")
            val = locs[key]
        elif op.startswith("STORE_"):
            key = op[6:].lower().replace("_", "")
            locs[key] = arg
        else:
            continue
        del code[op.argstart : op.offset]
    assert not code
    del env['__builtins__']  # Don't need built-in functions.


env = {"a": 3, "b": 42}
exec_bytecode(b"\x7f\xef\xff\xd8", env)

# ── Using ctors and dtors ─────────────────────────────────────────────────────

class CtorDtor:
    def __init__(self, value: int):
        self.value = value
        print("__new__() called with {}.".format(value))
    
    def __del__(self):
        print('__del__() called with {}'.format(self.value))

    def ctor_dtor(self) -> None:
        pass

c = CtorDtor(9)
d = CtorDtor(10)
CtorDtor.cctor()
CtorDtor.dctor()




# ── Struct and array classes ───────────────────────────────────────────────────

struct.pack('i', 1234)

array.array('L').frombytes(struct.pack('i', 1234))

assert isinstance(array.array('L'), MutableSequence)

assert isinstance(struct.Struct('<hhl').pack(-2, -1, 1, 2), bytes)
assert isinstance(struct.Struct('>hh').unpack_from(bytes([0xfimport re
import shutil
import sys
import tempfile
import time
import traceback
import types
import zipfile as zip_mod
from collections.abc import Callable, Iterator
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timedelta
from functools import partialmethod, wraps
from itertools import chain, product
from math import ceil, gcd as _gcd, log2, prod
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import randint
