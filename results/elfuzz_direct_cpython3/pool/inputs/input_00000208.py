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
)

import more_itertools
import numpy as np
import pandas as pd
import prettytable
import requests
from attrs import frozen
from docutils.nodes import literal_block
from markdownify import MarkdownConverter
from pyparsing import ParseException
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from seed02 import lazy_property


@frozen
class Timecode:
    """Timecode object."""

    hours: int = 0
    minutes: int = 0
    seconds: float = 0.0
    milliseconds: int = 0
    microseconds: int = 0
    nanoseconds: int = 0

    @classmethod
    def from_string(cls, timestr: str) -> Timecode:
        """Convert a string to a `Timecode` object."""
        try:
            hmsmstr = timestr.split(".")
            if len(hmsmstr) == 1:
                msstr = "0" * 3 + hmsmstr[0]
            elif len(hmsmstr) == 2:
                msstr = "0" + hmsmstr[1]
            else:
                raise ValueError("Invalid timecode format.")
            return cls(
                *[int(x) for x in "".join(msstr).split(":")],
                milliseconds=int(msstr[-3:]),
            )
        except Exception as e:
            raise ValueError(f"Invalid timecode '{timestr}' ({e})")

    def __add__(self, other: Timecode | float) -> Timecode:
        """Add two `Timecode` objects or an integer number of seconds."""
        if isinstance(other, self.__class__):
            return self.__class__(
                # integer addition
                (self.hours + other.hours)
                + (self.minutes + other.minutes)
                + (self.seconds + other.seconds),
                self.milliseconds + other.milliseconds,
            )
        if isinstance(other, (int, float)):
            return self.__class__(self.to_seconds() + other)
        raise TypeError()

    def __sub__(self, other: Timecode | float) -> Timecode:
        """Subtract two `Timecode` objects or an integer number of seconds."""
        if isinstance(other, self.__class__):
            return self.__class__(
                # integer subtraction
                (self.hours - other.hours)
                + (self.minutes -