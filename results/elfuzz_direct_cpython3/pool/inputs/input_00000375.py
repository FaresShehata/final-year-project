"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import io
import marshal
import pickle
import pickletools
import struct
import sys
import textwrap
import tracemalloc
import types
import weakref
from typing import Any

# ── Bytecode introspection ────────────────────────────────────────────────────

def annotated_disassembly(fn) -> str:
    buf = io.StringIO()
    dis.dis(fn, file=buf)
    return buf.getvalue()


def count_opcodes(fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for instr in dis.get_instructions(fn):
        counts[instr.opname] = counts.get(instr.opname, 0) + 1
    return dict(sorted(counts.items()))


def hot_path(n: int) -> int:         # deliberately simple for clear bytecode
    total = 0
    for i in range(n):
        if i % 2 == 0:
            total += i * i
        else:
            total -= i
    return total


# ── Code object surgery ───────────────────────────────────────────────────────

def clone_with_name(fn: types.FunctionType, new_name: str) -> types.FunctionType:
    """Return a copy of fn with a different __name__ embedded in its code."""
    co = fn.__code__
    # Python 3.8+ .replace() API
    new_co = co.replace(co_name=new_name)
    new_fn = types.FunctionType(
        new_co, fn.__globals__, new_name, fn.__defaults__, fn.__closure__
    )
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)



# ── Types and protocols ───────────────────────────────────────────────────────

_T = TypeVar('_T')
_Sensor = TypeVar('_Sensor', bound='Sensor')


class Sensor(_Protocol[_Sensors]):     # can be used as bounds on generic types
    reading: _Annotated[float, positive]


_Annotated = TypeVar('_Annotated', bound=Tuple[Any, ...])


def _validate_annotation(annotation: Any) -> TypeGuard[Tuple[Any, ...]]:
    return isinstance(annotation, tuple) and len(annotation) == 2 \
           and annotation[0] is Annotated \
           and isinstance(annotation[1], tuple) \
           and len(annotation[1])>0 \
           and all(isinstance(a, tuple) and len(a)==2 for a in annotation[1])

@overload
def Annotated[T_co, Annos:_Annotated](_annos:Annos) -> T_co:
    ...

@overload
def Annotated[T_co, Annos:_Annotated](_annos:Any) -> T_co:
    ...

def Annotated[T_co, Annos:_Annotated](annotation: Annos | None = None) -> Callable[[T_co], T_co]:
    """Like @typing.overload but for non-generic types.

    >>> @Annotated[int, "a", ("b", "c")]
    ... class Foo:
    ...     pass
    """
    if annotation is None or _validate_annotation(annotation):
        return lambda t: t
    elif _validate_annotation(annotation[1]):
        return lambda t: t
    else:
        raise TypeError("Invalid Annotated annotation")


def _implements_interface(cls: type, interface: type) -> bool:
    return cls in getattr(interface, '__implemented__', [])


class ImplementsInterface(Generic[_T]):
    __implementations__: ClassVar[List[Type]] = []
    __implemented__: ClassVar[List[Type]]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if not getattr(cls, '__abstract__', False):
            ImplementsInterface.__implementations__.append(cls)
            ImplementsInterface.__implemented__.append(cls)


# ── Weak references ───────────────────────────────────────────────────────────

class Foo:
    def __init__(self, num: int, val: str) -> None:
        self.num = num
        self.val = val

    def __repr__(self) -> str:
        returnimport shutil
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
from string import Formatter as Formatter_cls
from tokenize import TokenInfo
from typing import (
    Any, BinaryIO, ClassVar, Dict, Generic, Iterable, List, Literal, Mapping,
    MutableMapping, Match, Optional, Pattern, Tuple, TypedDict, TypeVar,
    Union, cast, overload
)
from typing_extensions import Final, Protocol, runtime_checkable, Concatenate
from uuid import UUID

if sys.version_info >= (3, 9): from collections.abc import AsyncGenerator, Awaitable
else:                           from async_generator import asynccontextmanager as asynccontextmanager
from concurrent.futures import ThreadPoolExecutor as FuturePool
from contextlib import suppress, redirect_stdout, AbstractContextManager
from contextvars import ContextVar
from pathlib import Path
from tempfile import TemporaryDirectory
from typing_extensions import get_args, get_origin, get_type_hints, get_origin, get_args, get_origin
from numbers import Integral
from contextlib import contextmanager
from contextvars import ContextVar
from enum import EnumMeta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import _eval_type, _type_vars, _make_class_def, TypeGuard, _eval_type, _type_vars, _make_class_def
from numbers import Integral
from contextlib import contextmanager
from enum import EnumMeta
from pathlib import Path
from tempfile import TemporaryDirectory
from abc import abstractmethod
from decimal import Decimal
from typing import Protocol, runtime_checkable, runtime_checkable, runtime_checkable, runtime_checkable



# ── Custom types ─────────────────────────────────────────────────────────────

def _parse_typeddict(typ: type[_T]):
    typ_var, attrs = _type_vars(typ).pop()
    return typ_var, attrs

_T = TypeVar('_T')

@runtime_checkable
class _Iterable(TypedDict):
    __mro_entries__: tuple[type[_T], ...]


@runtime_checkable

# ── Annotated constraints (runtime-checked via descriptor) ───────────────────

class _Constrained:
    """Descriptor that reads Annotated metadata to validate."""

    def __set_name__(self, owner, name):
        self.pub  = name
        self.priv = f"_{owner.__name__}__{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


def positive(x) -> bool:
    return isinstance(x, (int, float)) and x > 0

def short_str(x) -> bool:
    return isinstance(x, str) and len(x) <= 20


class Sensor:
    reading: Annotated[float, positive] = _Constrained()   # type: ignore[assignment]
