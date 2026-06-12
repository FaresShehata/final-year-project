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
import json
import math
import os
import pickle
import re
import random
import secrets
import signal
import string
import sys
import threading
import time
import types
import typing
import urllib.request as urlrequest
import zlib
from collections.abc import Iterable, Iterator
from datetime import timedelta
from functools import partial
from multiprocessing import Pool
from inspect import isawaitable, iscoroutinefunction, signature
from multiprocessing.sharedctypes import Value
from pprint import pformat
from queue import Empty, Queue
from reprlib import recursive_repr
from signal import Signals, SIGINT, SIGTERM
from socketserver import DatagramRequestHandler
from statistics import mean
from subprocess import PIPE, Popen, TimeoutExpired
from types import FrameType, TracebackType, SimpleNamespace
from typing import (
    Any,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    SupportsLessThan,
    Tuple,
    TypeVar,
    Union,
    runtime_checkable,
    overload,
)
from unittest.mock import Mock
from weakref import WeakKeyDictionary
from zoneinfo import ZoneInfo

import aiofiles
import asyncio
import cProfile
import concurrent.futures
import contextlib
import enum
import filecmp
import glob
import gzip
import http.client
import html.parser
import html.entities
import imghdr
import ipaddress
import keyword
import logging.handlers
import markdown
import mimetypes
import motor.motor_asyncio
import netifaces
import numpy as np
import oauth2client.client
import paramiko
import pydantic
import requests
import requests.models
import re
import rich.console
import rich.table
import rich.text
import rich.traceback
import rich.tree
import rich.repr
import rich.prompt
import rich.syntax
import rich.logging
import rich.panel
import rich.live
import rich.measure
import rich.align
import rich.highlighter
import rich.padding
import rich.rule
import rich.prompt
import rich.markdown
import rich.color
import rich.color_theme
import rich._text
from bs4 import BeautifulSoup
from colorama import Fore, Style
from dotenv import load_dotenv
from distutils.util import strtobool
from functools import lru_cache, wraps
from ftp.drive3.netdrive import FTPDrive3Client
from google.cloud.firestore_v1.async_query import Query
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf.json_format import MessageToDict
from google.protobuf.struct_pb2 import Struct
from hikari import User as HikariUser, GuildMember as HikariGuildMember
from hikari.api.interaction.response import InteractionResponseData
from hikari.events.guild_members_update_event import GuildMembersUpdateEvent
from hikari.errors import RateLimitTooLongError

class AsyncIterator(Generic[T]):
    def __aiter__(self):
        return self

    @overload
    async def __anext__(self: AsyncIterator[None]) -> None:
        ...

    @overload
    async def __anext__(self: AsyncIterator[T]) -> T:
        ...

    async def __anext__(self):
        """Return the next item from the iterator."""
        raise NotImplementedError("An `AsyncIterator` must implement `__anext__()`")


@runtime_checkable
class SupportsLessThan(Protocol[T]):
    def __lt__(self, other: object) -> bool:
        ...


@dataclasses.dataclass(slots=True)
class User:
    name: str
    username: str
    email: str | None = None
    password: str | None = None
    age: int | None = None
    is_active: bool | None = True
    friends: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError(f"{self.__repr__()}.name must be a string.")
        if not isinstance(self.username, str):
            raise TypeError(
                f"{self.__repr__()}.username must be a string."
            )
        if not isinstance(self.email, (str, type(None))):
            raise TypeError(f"{self.__repr__()}.email must be a string or None.")
        if not isinstance(self.password, (str, type(None))):
            raise TypeError(
                f"{self.__repr__()}.password must be a string or None."
            )
        if not isinstance(self.age, (int, type(None))):
            raise TypeError(f"{self.__repr__()}.age must be an integer or None.")
        if not isinstance(self.is_active, bool):
            raise TypeError(f"{self.__repr__()}.is_active must be a boolean.")

        self.friends.sort()


def get_random_user():
    while True:
        yield User(
            name=f"User {random.randint(1, 1_000_000)}",
            username=f"user_{random.randint(1, 1_000_000)}",
            email=f"user_{random.randint(1, 1_000_000)}@example.com",
            password="password",
