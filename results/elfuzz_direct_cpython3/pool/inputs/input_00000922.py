"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import gc
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import itertools
import os.path
import sys
import types
import typing
import traceback
import unittest
import uuid
import warnings
import weakref
import zlib
import struct
import timeit
import zipfile
import zipimport
import textwrap
import math
import platform
import pickle
import cPickle
import marshal
import copy_reg as copyreg
import _weakrefset as wfs
import io
import re
import array
import collections
import collections.abc
import collections.abc._callableiterator
import datetime
import decimal
import fractions
import hashlib
import heapq
import hmac
import io
import itertools
import json
import keyword
import linecache
import logging
import mmap
import multiprocessing.pool
import operator
import pathlib
import pprint
import random
import reprlib
import signal
import sqlite3
import stat
import string
import subprocess
import sysconfig
import threading
import time
import token
import tokenize
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import warnings
import weakref
import xmlrpc.client
import sysconfig
import asyncio
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import asyncio.futures
import asyncio.format_helpers
import asyncio.transports
import asyncio.queues
import async_generator
import asyncio.server
import asyncio.streams
import asyncio.proactor_events
import asyncio.sslproto
import asyncio.protocols
import asyncio.subprocess
import asyncio.trsock
import asyncio.unix_events
import asyncio.windows_events
import asyncio.base_events
import asyncio.events
import asyncio.futures
import asyncio.locks
import asyncio.runners
import asyncio.selector_events
import asyncio.tasks
import asyncio.unix_events
import asyncio.windows_events
import    )
    new_fn.__dict__.update(fn.__dict__)
    return new_fn


def change_code_object(fn: types.FunctionType, newco: types.CodeType) -> None:
    """Replace the code attribute of a function's .__code__ with newco."""
    fn.__code__ = newco


def add_to_globals(fn: types.FunctionType, to: set[str]) -> None:
    """Add all names from fn.__globals__ that aren't already in 'to' to 'to'."""
    for name, value in fn.__globals__.items():
        if isinstance(value, types.FunctionType):
            continue
        if name not in to:
            to.add(name)


def rename_module(mod: types.ModuleType, old_name: str, new_name: str) -> None:
    """Change mod.__name__ and mod.__file__ if necessary.

    This is done by replacing the module's filename or dirname (depending on whether it's an egg).
    """
    new_filename = mod.__spec__.origin.replace(old_name, new_name).rstrip(".pyw")
    if mod.__spec__.origin.endswith(new_filename):
        mod.__name__ = new_name      # don't need to touch this
        return
    # check for eggs
    if "/.egg-info/" in mod.__spec__.origin:
        idx = mod.__spec__.origin.rfind("/.egg-info/")
        assert idx > -1, "unexpected bad egg origin"
        prefix = mod.__spec__.origin[0:idx]
        new_spec = importlib.util.spec_from_file_location(new_name, new_filename)
        if not new_spec:
            raise ValueError(f"cannot create spec for {new_name} at {new_filename}")
        new_mod = importlib.util.module_from_spec(new_spec)
        new_spec.loader.exec_module(new_mod)
        new_mod.__name__ = new_name   # replace the module itself
        mod.__name__ = new_name       # replace the package containing it
        mod.__path__ = new_spec.submodule_search_locations  # update the path
    else:
        # load new module instance based on origin
        new_spec = importlib.util.spec_from_file_location(new_name, new_filename)
        if not new_spec:
            raise ValueError(f"cannot create spec for {new_name} at {new_filename}")
        new_mod = importlib.util.module_from_spec(new_spec)

        # replace globals in the new module with those from the old one
        load    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
