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

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    requests:   int


# ── ClassVars ────────────────────────────────────────────────────────────────

class Color(NamedTuple):
    r: int; g: int; b: int; a: int = 255


class Settings(Generic[T]):
    default_value: T
    values: tuple[T, ...]
    
    def __init__(self, value: T) -> None:
        self.value = value
    
    def __repr__(self) -> str:
        return f"<{type(self).__name__} value={repr(self.value)}>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value

    @classmethod
    def with_values(cls, *values: T) -> ClassVar[Settings[T]]:
        """Create class variable."""
        return cls(values[-1])
    

def foo() -> None:
    ...


# ── Funcs ───────────────────────────────────────────────────────────────────

def is_positive(number: int) -> bool:
    return number > 0


def parse_json(json_str: str) -> JsonValue:
    try:
        json_obj = ast.literal_eval(json_str)
        
        if not isinstance(json_obj, (dict, list)):
            raise ValueError(f"Invalid JSON: {json_obj}")
            
        return json_obj
    except Exception:
        raise ValueError("Failed to parse JSON.")


def merge_dicts(*dicts: dict[str, JsonValue]) -> dict[str, JsonValue]:
    merged_dict = {}
    
    for d in dicts:
        for key, val in d.items():
            merged_dict[key] = val
            
    return merged_dict


def print_progress_bar(iteration: int, total: int, prefix: str = "", suffix: str = "",
                       decimals: int = 1, length: int = 100, fill: str = "█") -> None:
    percent = ("{:." + str(decimals) + "f}").format(100.0 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
    # Print New Line on Complete
    if iteration == total:
        print()


def format_string(msg: str, **kwargs: str) -> str:
    formatter = string.Formatter()
    return formatter.vformat(msg, (), kwargs)


def print_with_thread_id(msg: str) -> None:
    thread_id = threading.get_ident()
    print(thread_id, msg)


def print_with_time_and_thread_id(msg: str) -> None:
    thread_id = threading.get_ident()
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(timestamp, thread_id, msg)


def print_with_thread_id_and_file_name(msg: str) -> None:
    thread_id = threading.get_ident()
    file_name = os.path.basename(__file__)
    print(thread_id, file_name, msg)

