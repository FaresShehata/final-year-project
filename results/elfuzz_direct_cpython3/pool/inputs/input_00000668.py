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
import itertools as it
import os
import pickle
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings
import weakref
from collections.abc import Callable, Generator, Hashable, Iterable, Iterator, Mapping, MutableMapping, Sequence
from contextlib import suppress
from dataclasses import Field, fields, is_dataclass, _field_info
from functools import partialmethod, wraps, singledispatch, cached_property
from html.parser import HTMLParser, HTMLTreeBuilder
from math import ceil, floor, log10
from multiprocessing.pool import Pool as MultiPool
from queue import Queue
from random import Random, randrange, shuffle, seed
from socket import AF_INET, SOCK_STREAM, socket
from statistics import mean
from threading import BoundedSemaphore, Lock, Thread, current_thread, enumerate, Event, local
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    AsyncGenerator,
    ClassVar,
    Generic,
    Literal,
    NoReturn,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeGuard,
    Union,
)
from typing_extensions import (
    Concatenate,
    Final,
    GetItem,
    GetAttr,
    ParamSpec,
    Self,
    SupportsIndex,
    Unpack,
    override,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


__all__ = [
    "AsyncQueue",
    "BoundedSemaphore",
    "Cache",
    "CallCount",
    "CallLog",
    "CmpKey",
    "Counter",
    "CSVParser",
    "DataClass",
    "DATA_CLASS_FIELDS",
    "DEFAULT_DATA_CLASS_FIELDS",
    "DefaultDict",
    "ensure_path_exists",
    "ensure_path_not_exist",
    "FlattenIterable",
    "get_class_attrs",
    "get_dataclass_fields",
    "get_dotted_attr",
    "get_file_size",
    "get_free_space",
    "get_fullpath",
    "get_loaded_modules",
    "get_module_globals",
    "get_module_methods",
    "get_root_dir",
    "groups_to_dict",
    "hash_object",
    "info_from_json",
    "is_base64_encoded",
    "is_csv_header_row",
    "is_iterable",
    "is_list_like",
    "is_mutable_mapping",
        self.label   = label
        self.reading = reading

    def __repr__(self):
        return f"Sensor({self.label!r}, {self.reading})"


# ── NamedTuple ────────────────────────────────────────────────────────────────

class Span(NamedTuple):
    start: int
    end:   int
    label: str = ""

    def length(self) -> int:
        return self.end - self.start

    def overlap(self, other: Span) -> int:
