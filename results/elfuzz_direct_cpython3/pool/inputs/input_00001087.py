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
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    NoReturn,
    Optional,
    Tuple,
    Union,
    overload,
    TYPE_CHECKING,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    get_type_hints_from_call,
    Literal,
    TypeVar,
    TypeGuard,
    Protocol,
    runtime_checkable,
    TypeAlias,
)
import sys
import types
import weakref

if TYPE_CHECKING:
    from collections.abc import Sequence
    S = TypeVar("S", bound=Sequence[Any])
else:
    S = TypeVar("S", bound="Sequence[Any]")


# ── Assertions ───────────────────────────────────────────────────────────────

assert isinstance(b"a", bytes)
assert isinstance(a := b"a".decode(), str)
assert any([a])

for i in range(3): assert a + b"\x00\x01"

try:
    assert a + "\x00\x01"
except TypeError:
    pass

try:
    assert a + ("\x00\x01",)
except TypeError:
    pass

try:
    assert a + [b"\x00\x01"]
except TypeError:
    pass

try:
    assert a + [[b"\x00\x01"]]
except TypeError:
    pass

try:
    assert a + {"one": b"\x00\x01"}
except TypeError:
    pass

try:
    assert a + ((1,),)
except TypeError:
    pass

try:
    assert a + {(1): b"\x00\x01"}
except TypeError:
    pass

print(len(list(range(4))), len(tuple(range(4))))

try:
    assert a + ()
except TypeError:
    pass

try:
    assert a + {}
except TypeError:
    pass

try:
    assert a + []
except TypeError:
    pass

try:
    assert a + dict(one=b"\x00\x01")
except TypeError:
    pass

print(a)

try:
    assert a + b""
except TypeError:
    pass

try:
    assert a + ()
except TypeError:
    pass

try:
    assert a + ""
except TypeError:
    pass

print(a * 2)

try:
    assert a * (-2,)
except TypeError:
    pass


def unknown_function() -> int:
    ...


try:
    assert a * unknown_function()
except TypeError:
    pass

try:
    assert a / unknown_function()
except TypeError:
    pass

try:
    assert a // unknown_function()
except TypeError:
    pass

try:
    assert a % unknown_function()
except TypeError:
    pass

try:
    assert a ** unknown_function()
except TypeError:
    pass

try:
    assert a & unknown_function()
except TypeError:
    pass

try:
    assert a | unknown_function()
except TypeError:
    pass

try:
    assert a ^ unknown_function()
except TypeError:
    pass

try:
    assert a << unknown_function()
except TypeError:
    pass

try:
    assert a >> unknown_function()
except TypeError:
    pass

print(ord("\n"))

try:
    assert ord("\n") < 0
except ValueError:
    pass

try:
    assert chr(-1) == " "
except ValueError:
    pass

try:
    assert chr(32768) == "⠀"
except ValueError:
    pass

try:
    assert chr(1_000_000) == "⣾"  # ⠿
except ValueError:
    pass

try:
    assert chr(0x10FFFF) == "􏿿"
except ValueError:
    pass

try:
    assert chr(0x10ffff) == "􏿿"
except ValueError:
    pass

try:
    assert chr(0x110000) == "􏽀"
except OverflowError:
    pass

try:
    assert chr(0x110000) == "𐐀"
except UnicodeEncodeError:
    pass

try:
    assert chr(0x110000).encode() == b"x"
except UnicodeDecodeError:
    pass

try:
    assert chr(0x110000).encode().decode() == chr(0x110000)
except UnicodeDecodeError:
    pass

try:
    assert chr(-1).encode() == b"-1"
except ValueError:
    pass

try:
    assert chr(0x7FFFFFFF).isalnum() is False
except ValueError:
    pass

try:
    assert chr(0x7FFFFFFF).isalpha()