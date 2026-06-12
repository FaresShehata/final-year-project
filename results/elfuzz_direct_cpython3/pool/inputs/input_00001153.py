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
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

JsonDict: TypedDict(
    "JsonDict",
    {
        str: "Union[int, float, str, bool, None, List['JsonDict']]"
        # or ValueType
    }
)
EnumValues: TypeAlias = tuple[
    "str" | tuple["str"],
    tuple[tuple["str"], ...],
    tuple[tuple["str", ...]]
]
ClassInfo: TypedDict(
    "ClassInfo",
    {
        "name": "Type[T]",
        "classname": "typing_extensions.ClassInfo",
        "module": "str",
        "bases": "tuple[Type[Any]]"
    }
)

# ── Enum ────────────────────────────────────────────────────────────────────

class Color(NamedTuple):
    name: str
    code: tuple[int, int, int]


color_names: tuple[str] = ("red", "green", "blue")


color_codes: tuple[tuple[int, int, int]] = (
    (178, 34, 93), (34, 178, 93), (34, 93, 178)
)


colors: tuple[Color] = tuple(Color(name, code) for name, code in zip(color_names, color_codes))


enum_class: Final[list[type[Any]]] = [type(v) for v in dir(string) if not v.startswith("_")]
enum_class.extend([type(v) for v in dir(string.ascii_letters)] + [type(v) for v in dir(string.digits)])

# ── ParamSpec ────────────────────────────────────────────────────────────────

ParamSpecT_P: TypeVar("ParamSpecT_P", covariant=True, bound=Parameter)
ParamSpecT_KV_P: TypeVar("ParamSpecT_KV_P", covariant=True, bound=Parameter)
ParamSpecT_V_P: TypeVar("ParamSpecT_V_P", covariant=True, bound=Parameter)
ParamSpecT_S_P: TypeVar("ParamSpecT_S_P", covariant=True, bound=_S_ParamSpecT_S_P)
ParamSpecT_I_P: TypeVar("ParamSpecT_I_P", covariant=True, bound=Iterable[_I_TypeHint])

_I_TypeHint: TypeVar("_I_TypeHint", covariant=True, bound=object)
_S_ParamSpecT_S_P: ParamSpec["_S_ParamSpecT_S_P"]

# ── PEP-0655 ────────────────────────────────────────────────────────────────<|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|><|fim_pad|>

# ── get_type_hints ───────────────────────────────────────────────────────────

def _annotated_is_annotated(annotated: type[Any]) -> bool:
    return hasattr(annotated, "__origin__") and annotated.__origin__ == Annotated


def _annotated_get_args(annotated: type[Any]) -> tuple[type[Any], ...]:
    origin = getattr(annotated, "__origin__", object)

    if origin != Annotated:
        raise ValueError("Must be an 'Annotated' type.")
    else:
        args = getattr(annotated, "__args__")

        if len(args) < 2:
            raise ValueError("Requires at least two arguments.")

        return args


def _annotate_arg(arg: type[Any], annotation: type[Any]) -> type[Any]:
    if arg in enum_class:
        return arg
    elif _annotated_is_annotated(annotation):
        return _annotate_arg(annotation, annotation.__args__[0])
    else:
        return annotation


