"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations
import base64
import binascii
import collections
import dataclasses
import functools
import inspect
import itertools
import json
import logging
import math
import os
import pathlib
import random
import re
import socket
import subprocess
import threading
import time
import typing
import uuid
import warnings
from functools import partial
from io import BytesIO
from types import TracebackType
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from urllib.parse import urlparse
from weakref import WeakSet

import aiohttp
import anyio
import astroid
import base58
import black
import colorama
import colorlog
import commonmark
import cProfile
import cytoolz
import decorator
import dotenv
import eth_abi
import eth_utils
import fuzzywuzzy
import h11
import ipaddress
import jinja2
import lazy_object_proxy
import markupsafe
import more_itertools
import numpy
import openai
import pycodestyle
import pydantic
import pygments
import pygments.lexers
import pytest
import requests
import rich
import requests_cache
import requests_mock
import sqlalchemy
import sqlparse
import tabulate
import textwrap
import tomli
import tomllib
import tomlkit
import tomlkit.exceptions
import trio
import ujson
import unidecode
import uvicorn
import yaml
import yarl
from bs4 import BeautifulSoup
from httpx import AsyncClient
from packaging.version import Version
from pydantic import BaseModel
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.table import Table
from rich.time import TimeDelta
from rich.text import Text
from starlette.requests import Request
from starlette.responses import Response

from . import constants as C

if False:
    from .typing import (  # noqa
        AnyCallable,
        AnyEnum,
        AnyIterable,
        AnyMapping,
        AnySequence,
        AnyTuple,
        AnyValue,
        AsyncIterator,
        AsyncGenerator,
        CallableT,
        CoroFunc,
        Coroutine,
        DictAny,
        EnumT,
        Generator,
        Iterator,
        ListAny,
        OptionalStr,
        PathLike,
        SequenceAny    """
    try:
        await coroutine
    except Exception as e:
        raise e from None


async def wrap_with_context_manager(loop: asyncio.AbstractEventLoop, coro: Awaitable[T]) -> T:
    """Wraps an event loop with a context manager for easier error handling.

    Args:
      loop: Event loop.
      coro: Coroutine object to be executed.

    Returns:
      Return value of the coroutine.

    Raises:
      Any exception raised by the coroutine or `loop.run_forever()`.

    """

    async with loop.create_task(coro) as task:
        if task.exception():
            raise task.exception()
        else:
            return task.result()


async def run_coroutine_in_background(loop: asyncio.AbstractEventLoop, coro: Awaitable[T]) -> T:
    """Starts a new background thread to run the given coroutine asynchronously.

    Args:
      loop: Event loop.
      coro: Coroutine object to be executed.

    Returns:
      Return value of the coroutine.

    Raises:
      Any exception raised by the coroutine or `loop.run_forever()`.

    """
    task = loop.create_task(coro)
    task.add_done_callback(lambda _: loop.stop())
    await task


async def fully_run_async_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Waits until all tasks have been cancelled and then stops the event loop.

    This function is useful when you want to ensure that all pending tasks have completed before stopping the event loop.

    Args:
      loop: Event loop.

    Examples:

        from src.utils.async_utils import fully_run_async_loop

        async def main() -> None:
            ...

        loop = asyncio.get_event_loop()

        loop.create_task(main())  # Start the coroutine in a separate task
        await fully_run_async_loop(loop)  # Wait until all tasks have finished


    """

    while loop.is_running():
        await asyncio.sleep(0.        total += x
        return total

    return acc


def memoize_rec(fn: Callable) -> Callable:
    """Memoisation decorator that handles recursive calls correctly."""
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]

    return wrapper


# ── Trampolining ──────────────────────────────────────────────────────────────

class Thunk:
    __slots__ = ("fn", "args")

    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args


def trampoline(f) -> Callable:
    @functools.wraps(f)
    def wrapper(*args):
