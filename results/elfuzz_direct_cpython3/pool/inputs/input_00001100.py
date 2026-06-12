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
PP  = ParamSpec("PP")

P  = ParamSpec("P")
R  = ParamSpec("R")


# ── Temporary file management ────────────────────────────────────────────────

def temp_file(suffix: str | None = None, /, *, encoding: str | None = "utf-8") -> str:
    """Create and open a temporary file for writing."""
    if suffix is None:
        suffix = ""
    with tempfile.NamedTemporaryFile(
        mode="w", prefix="seed005_", suffix=suffix, delete=False, encoding=encoding
    ) as fp:
        path = fp.name
    return path


# ── String formatting ────────────────────────────────────────────────────────

class MyStringFormatter(textwrap.TextWrapper):

    def fill(self, string: str, width: int, **options) -> str:
        options.setdefault("replace_whitespace", True)
        if "break_long_words" not in options or options["break_long_words"]:
            options.setdefault("subsequent_indent", "")
        return super().fill(string, width, **options)


my_formatter = MyStringFormatter(width=79)


# ── Nested loops ────────────────────────────────────────────────────────────


NestedLoop = list[list[Any]]
nested_loop: NestedLoop = [[], []]
nested_loop.append(nested_loop[0])


# ── Decorators ───────────────────────────────────────────────────────────────


def print_table(table: list[list[str]], *,
                header: bool = True, sep: str = "\t",
                align: dict[int, Literal[-1, 0, 1]] = {0: -1},
                line_length: int = 80):
    """
    Print data table in a neatly aligned format.

    >>> print_table([['a', 'b'], [1, 2]])
    a b
    1 2
    """

    if isinstance(table, dict):
        keys = sorted(list(table.keys()))
        rows = [(key,) + tuple(row[key] for row in table.values()) for key in keys]
        table = rows

    col_widths = []
    if header:
        col_widths = [max(len(str(row[i])) for row in table) for i in range(len(table[0]))]
        for i in range(len(col_widths)):
            col_widths[i] += len(next(iter(table[0])))
    else:
        col_widths = [len(max((row[i] for row in table), key=len)) for i in range(len(table[0]))]

    # Determine column alignments.
    align = {}
    for i, (width, char) in enumerate(zip(col_widths, sep)):
        if i < len(table[0]):
            if table[0][i] == "":
                align[i] = -1
            elif align.get(i) != -1:
                if align[i] > 0:
                    align[i] = max(align.get(i), width // 2)
                elif align[i] <= 0:
                    align[i] = min(align.get(i), width // 2)
        else:
            align[i] = 0

    # Pad columns to specified widths.
    for j in range(len(table[0])):
        pad_start = 0
        pad_end = 0
        if align[j] == 1:
            pad_end = col_widths[j] - len(table[0][j])
        elif align[j] == -1:
            pad_start = col_widths[j] - len(table[0][j])
        elif align[j] >= 0 and align[j] < 0:
            pad_start = col_widths[j] - len(table[0][j]) // 2 - 1
            pad_end = col_widths[j] - len(table[0][j]) // 2
        elif align[j] <= 0 and align[j] > 0:
            pad_start = col_widths[j] - len(table[0][j]) // 2
            pad_end = col_widths[j] - len(table[0][j]) // 2 + 1
        for i, row in enumerate(table[:]):
            if i == 0 and header:
                continue
            row[j] = (f"{table[0][j]}" + f"{str(row[j]):<{pad_start}}" +
                      f"{str(row[j]):>{pad_end}}")
            if i == 0 and header and align[j] >= 0:
                row[j] = f"{'|' if i > 0 else ''}{row[j]:^{col_widths[j]}s}"
            else:
                row[j] = f"{row[j]:{col_widths[j]        return getattr(obj, self.priv, None)

    def __set__(self, obj, value):
        hints = get_type_hints(type(obj), include_extras=True)
        ann   = hints.get(self.pub)
        if ann and hasattr(ann, "__metadata__"):
            for constraint in ann.__metadata__:
                if callable(constraint):
                    if not constraint(value):
                        raise ValueError(f"{self.pub}={value!r} fails constraint")
        setattr(obj, self.priv, value)


