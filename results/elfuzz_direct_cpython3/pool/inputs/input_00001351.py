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
import types
import warnings
from abc import ABCMeta
from collections import (
    ChainMap,
    Counter,
    deque,
    OrderedDict,
    namedtuple,
    UserDict,
    UserList,
    UserString,
)
from concurrent.futures import Future as ConcurrentFuture
from contextlib import suppress
from functools import cached_property, partialmethod, reduce
from inspect import Parameter, Signature, signature
from itertools import chain, count, cycle
from pathlib import Path
from numbers import Integral, Real
from types import MappingProxyType
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    TypeAlias,
    overload,
)
from urllib.parse import quote_plus
from uuid import UUID

try:
    from typing_extensions import Protocol
except ImportError:  # pragma: no cover
    from typing import _Protocol as Protocol

warnings.filterwarnings("ignore", category=DeprecationWarning)


# ─── SEED 02 ────────────────────────────────────────────────────────────────────

warnings.simplefilter(action="ignore")


class Example:
    pass


example = Example()


async def main() -> None:

    print(1 + 1)

    a = "a"
    b = "b"
    c = f"{a} {b}"
    d = {"a": "b"}
    e = (c, d)
    f = [e]
    g = {f}
    h = set([g])
    i = tuple(h)
    j = list(i)
    k = dict(j)
    l = frozenset(k)

    assert type(l) is frozenset and len(l) == 1 and next(iter(l)) == {"a": "b"}

    assert isinstance(example, Example)
    assert issubclass(example.__class__, Example)
    assert issubclass(type(example), Example)
    assert issubclass(Example, object)

    assert str(c).endswith(f" {b}")
    assert repr(d) == f"<dict at 0x{id(d):x}>"

    assert hash(e) != hash(f)
    assert hash(g) == hash(f)
    assert hash(h) == hash(f)
    assert hash(i) == hash(f)
    assert hash(j) == hash(f)
    assert hash(k) == hash(f)
    assert hash(l) == hash(f)

    assert all(isinstance(x, int) for x in range(-5, 6))
    assert any(isinstance(x, float) for x in range(-5, 6))

    assert not False or True
    assert not True or False
    assert not True and True
    assert not True and False

    assert not False ^ True
    assert not True ^ False

    assert bool(True | False) == True
    assert bool(False & True) == False
    assert bool(True ^ False) == True
    assert bool(False ^ True) == True
    assert bool(not True) == False
    assert bool(not False) == True

    assert not not True
    assert not not False
    assert not not True and not not False
    assert not not True or not not False

    assert bool(None) == False
    assert bool({}) == False
    assert bool([]) == False
    assert bool((None,) * 3) == False
    assert bool("") == False

    assert int(1.499) == 1
    assert int(-1.499) == -1