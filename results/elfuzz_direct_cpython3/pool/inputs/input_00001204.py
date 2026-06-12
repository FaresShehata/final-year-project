"""
Seed 01 — OOP, metaclasses, descriptors, decorators, context managers, generators
"""

from __future__ import annotations

import abc
import contextlib
import functools
import itertools
import operator
import sys
import types
import weakref
import typing as t
import typing_extensions as te
from collections.abc import Iterable, Iterator, Mapping, Sequence
from enum import Enum
from functools import lru_cache
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeAlias,
    Union,
)

from . import typing_extras





""" 🥑 Types """

# ╭── String ───────────────────────

_TypeString = TypeVar("_TypeString", bound=str, covariant=True)



# ╰── Int ─────────────────────────

_TypeInt = TypeVar("_TypeInt", bound=int, covariant=True)





# ╭── Function ─────────────────────

_Function = TypeVar("_Function", bound=Callable[..., Any])



# ╰── Tuple ────────────────────────
TupleStrAny: TypeAlias = tuple[str, ...]






""" 🍎 Generics """

# ╭── Generic ──────────────────────

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


class Generic(Tuple[Union[_T1, _T2, _T3, _T4]]):
    pass




# ╰── Generic with extra methods ─────

_T5 = TypeVar("_T5", bound="Generic[...]")
_T6 = TypeVar("_T6", bound="Generic[...]")

_GenericWithMethod: TypeAlias = TypeVar(
    "_GenericWithMethod",
    bound="Generic[Optional[_T5], Optional[_T6]]"
)




# ── class MyClass ───────────────────────────────────────────────────────────

_TypingExtras = TypeVar("_TypingExtras", bound="typing_extras.TypingExtras")

class TypingExtras(_TypingExtras):
    pass


# ── class MyClass ────────────────────────────────────────────────────────────

_T5 = TypeVar("_T5", bound="MyClass[String]", covariant=True)
_T6 = TypeVar("_T6", bound="MyClass[Int]", contravariant=True)


class MyClass[T7](Generic[T7]):
    def __init__(self, arg: T7) -> None:
        self.arg: T7 = arg
    
    @classmethod
    def of(cls: type["_T5"], *args: T7) -> _T5:
        return cls(args) # type: ignore
    


# ── class MySubclass ─────────────────────────────────────────────────────────

_T7 = TypeVar("_T7")

class MySubclass(MyClass[_T7], Generic[_T7]):
    pass


# ── class MyClassWithExtraMethods ────────────────────────────────────────────

class MyClassWithExtraMethods:
    def __init__(self, arg: int) -> None:
        self.arg: int = arg

    def add(self, other: int) -> int:
        return self.arg + other



# ── class BaseClass ─────────────────────────────────────────────────────────