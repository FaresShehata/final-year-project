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
import os
import re
import shutil
import sys
import tempfile
import time
import types
import unittest.mock as mock
import urllib.request
from collections.abc import Iterable, Sequence
from functools import wraps
from io import StringIO
from io import TextIOWrapper
from itertools import chain, repeat, tee
from multiprocessing import Pool
from pathlib import Path
from pprint import pformat
from random import choice, randint, seed
from re import Match, Pattern, findall, split, sub
from re import escape as regex_escape
from signal import SIG_DFL, SIGINT, Signals, signal
from typing import (
    Any,
    Callable,
    ClassVar,
    Counter,
    Dict,
    FrozenSet,
    Generator,
    Generic,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
)
from typing_extensions import Self
from zlib import crc32


def _split_lines(
    source: str | bytes | None = None,
    keepends: bool = False,
    maxsplit: int | None = -1,
) -> list[str]:
    if isinstance(source, str):
        return source.splitlines(keepends=keepends, maxsplit=maxsplit)
    elif isinstance(source, bytes):
        return source.decode().splitlines(keepends=keepends, maxsplit=maxsplit)
    else:
        raise ValueError("Invalid argument type")


if sys.version_info >= (3, 9):
    from string import Formatter as _Formatter

    class _StringTemplate(_Formatter):
        def substitute(self, *args, **kwargs):
            try:
                result = super().substitute(*args, **kwargs)
            except KeyError as exc:
                raise ValueError(f"Missing substitution: {exc}") from exc
            return result

else:

    class _StringTemplate(object):
        def __init__(self, template: str) -> None:
            self._template = template

        def substitute(self, mapping: dict[str, Any]) -> str:
            # We use a regular expression to do the work.
            # The pattern matches each word of the format field and anything
            # that is not alphanumeric or '_'.
            non_word_chars_re = r"\W"

            def repl(match_obj: Match[str]) -> str:
                key = match_obj.group()
                value = mapping.get(key, "")
                return f"{value}"

            return re.sub(non_word_chars_re, repl, self._template)


def split_text(
    source: str |