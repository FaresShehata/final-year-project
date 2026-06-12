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
import asyncio as aio
import concurrent.futures as cfut
import io
import json
import logging
import math
import marshal
import multiprocessing as mp
import os
import random
import re
import threading
import time
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence
from functools import partial
from inspect import isawaitable
from itertools import chain
from pathlib import Path
from types import TracebackType
from typing import (
    Any, Generic, cast, ClassVar, Final, Literal, NoReturn, ParamSpec,
    TextIO, TypedDict, Protocol, runtime_checkable, overload, TypeVar, TypeGuard, Union, AsyncIterator, Awaitable
)

import bs4.element
import docutils.core
import docutils.nodes
import docutils.parsers.rst.directives.misc
import docutils.utils
import funcy
import jinja2
import lxml.etree
import requests as reqs
from ast import literal_eval as eval_ast_literal
from concurrent.futures.process import BrokenProcessPool
from functools import wraps
from hashlib import sha1 as hash_sha1
from hashlib import sha3_224 as hash_sha3_224
from inspect import Parameter, Signature
from operator import add
from pathlib import Path
from pprint import pformat
from queue import Empty, Queue
from sys import stderr, stdin, stdout
from textwrap import dedent
from textwrap import indent as wrap_indent
from textwrap import shorten as wrap_shorten
from textwrap import TextWrapper as WrapText
from textwrap import TextWrapper as ShortWrapText
from typing_extensions import Concatenate, ParamSpecArgs, ParamSpecKwargs, Self
from weakref import WeakSet

from .misc import decorators, fstrings, strint
from .repl import repl

# TODO: test bytearray in-place operations


def _seed():
	"""Run this to seed the RNG."""
	random.seed(1)


_seed()


@overload
def randrange(
		start: int | float | None = ...,
		stop: int | float | None = ...,
		step: int | float | None = ...,
	) -> int:
	pass


@overload
def randrange(*args: int | float, **kwargs: int | float) -> int:
	pass


def randrange(*args, **kwargs):
	return random.randrange(*args, **kwargs)


randrange.__doc__ = f"""