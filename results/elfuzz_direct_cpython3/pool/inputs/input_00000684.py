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
import timeit
import types
import typing
import typing_extensions as te
import urllib.parse
import warnings
from abc import abstractmethod, ABCMeta
from collections.abc import (
    MutableMapping,
    Sequence,
)
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from itertools import chain, cycle, tee
from operator import itemgetter
from pathlib import Path
from pprint import pformat
from random import sample
from re import Pattern
from sys import argv
from types import CodeType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Optional,
    Tuple,
    TypedDict,
    TypeVar,
)
from uuid import UUID
from typing_extensions import (
    Self,
    Unpack,
    assert_never,
    Annotated,
    ParamSpec,
    Concatenate,
    TypeGuard,
)
from urllib.parse import urlparse

import csvkit
import numpy as np
from IPython.display import display, Markdown, clear_output
from IPython.utils.io import capture_output, capture_stdin
from ipywidgets.widgets import Dropdown, Button, Layout
from pathtools.path import PathLike
from pydantic import BaseModel, Field, parse_obj_as, validator
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import track
from rich.text import Text
from rich.syntax import Syntax
from rich.align import Align
from rich.console import RenderGroup, Console, Group, ConsoleOptions
from rich.padding import Padding
from rich.style import Style
from rich.markup import escape
from rich.live import Live
from rich.panel import Panel
from rich.traceback import Traceback
from rich.jupyter_display import JupyterDisplay
from rich.jupyter_display import RichObject
from rich.highlighter import Highlighter
from rich.jupyter_display import RichText
from rich.console import group
from rich.box import DOUBLE_FRAME
from rich.padding import Padding
from rich.columns import Columns
from rich.progress import Progress, Track
from rich.prompt import Prompt, PromptSession
from rich.repr import rich_repr
from rich.rule import Rule
from rich.segment import Segment
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.terminal_theme import TerminalTheme
from rich.theme import Theme
from rich.console import ConsoleRenderable
from rich.console import ConsoleSettings
from rich.console import RenderGroup
from rich.console import ConsoleOptions
from rich.console import ConsoleSize
from rich.console import ConsoleWidth
from rich.console import ColorSystem
from rich.console import ConsoleWidths
from rich.console import ConsoleWrapper
from rich.console import LineWrapStrategy
from rich.console import RawConsole
from rich.console import TabularConsole
from rich.console import UnicodeDecoder
from rich.console import UnicodeEncoder
from rich.console import AnsiCode
from rich.console import AnsiRenderInfo
from rich.console import AnsiTerminalBuffer
from rich.console import ANSI_ESCAPE_REGEX
from rich.console import ANSI_ESCAPE_REGEX_ML
from rich.console import ANSI_ESCAPE_SEQUENCE_MATCHER
from rich.console import ANSI_ESCAPES
from rich.console import ANSI_ESCAPES_REVERSE
from rich)

if TYPE_CHECKING:
    pass  # keep TYPE_CHECKING branch exercised

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")

# ── Enums ─────────────────────────────────────────────────────────────────────

class Status(enum.Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    SUCCESS   = "success"
    FAILED    = "failed"
    CANCELLED = "cancelled"

    def is_terminal(self) -> bool:
        return self in {Status.SUCCESS, Status.FAILED, Status.CANCELLED}


class Priority(enum.IntEnum):
    LOW    = 1
    NORMAL = 5
    HIGH   = 10
    URGENT = 20


class Flag(enum.Flag):
    READ    = enum.auto()
    WRITE   = enum.auto()
    EXECUTE = enum.auto()
    RWX     = READ | WRITE | EXECUTE


# ── Protocols ─────────────────────────────────────────────────────────────────

@runtime_checkable
class Serialisable(Protocol):
    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, data: dict) -> "Serialisable": ...


@runtime_checkable
class Runnable(Protocol):
    async def run(self) -> str: ...


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclasses.dataclass(order=True, frozen=False, slots=True)
class Point:
    x: float
    y: float

    def distance(self, other: Point) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclasses.dataclass
class Task:
    id: int
    name: str
    priority: Priority = Priority.NORMAL
    status: Status = dataclasses.field(default=Status.PENDING)
    tags: list[str] = dataclasses.field(default_factory=list)
    metadata: dict = dataclasses.field(default_factory=dict)
    _history: list[Status] = dataclasses.field(default_factory=list, repr=False)

    # comparison key ignores status
    sort_key: int = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "sort_key", -int(self.priority))

    def transition(self, new_status: Status) -> None:
        self._history.append(self.status)
        self.status = new_status

    def to_json(self) -> str:
        return json.dumps({
