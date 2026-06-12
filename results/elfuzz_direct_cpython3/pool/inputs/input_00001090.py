"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import collections.abc as c_abc
import functools
import inspect
import operator
import os
import platform
import random
import reprlib
import re
import signal
import stat
import string
import subprocess
import sys
import threading
import traceback
import types
import warnings
from abc import ABCMeta, abstractmethod
from concurrent.futures import Future
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from email.message import Message
from itertools import chain, cycle, islice, repeat, tee
from math import e, pison
Message# Reply with a message object will be sent to the recipient.
Reply with an email message or a multipart MIME body.
The sender’s address is always the sender’s email address.

Send a system command to the operating system. The default implementation uses the OS-specific system command processor.

When used without arguments, print the last line of the standard error stream followed by a newline. Otherwise, write the arguments to the standard error stream (as with print).

Write out more debugging information when encountered during execution.
This function is intended to be called only within debuggers like pdb.

Print a trace back showing where you are currently executing your program. The first argument is the tracing level; higher values show deeper levels of the call stack.
Detail about tracing may vary by debugger. Some possible details include the number of nested indentation levels, a description of each call on the stack, the current state of local variables, etc.


OS system calls:

os.access(path, mode): Check whether the user has permission to access path according to mode (see os.F_OK, os.R_OK, os.W_OK, and os.X_OK).
os.chdir(dir): Change the current working directory to dir. If the directory does not exist, it raises FileNotFoundError.
os.chdir(): Return the absolute pathname of the current working directory.
os.listdir(directory): Return a list containing the names of the entries in directory.
os.mkdir(path): Create a new directory at path.
os.makedirs(path): Create a leaf directory and all intermediate ones.
os.mknod(path): Create a special file at path.
os.path.abspath(filename): Return the canonicalized absolute pathname of the specified filename.
os.path.basename(path): Return the final component of a pathname.
os.path.commonprefix(list): Return the longest string present in both operands.
os.path.dirname(path): Return the directory portion of a pathname.
os.path.exists(path): Test whether a path exists.
os.path.expanduser(path): Convert Unix-shell-style home-directory expansion sequences in path to an absolute path.
os.path.expandvars(path): Expand shell variable references in path.
os.path.getatime(path): Return the last access time of a path.
os.path.getmtime(path): Return the last modification time of a path.
os.path.isabs(path): Return True if the path is absolute.
os.path.isfile(path): Return True if path is an existing regular file.
os.path.isdir(path): Return True if path is an existing directory.
os.path.join(*args): Join one or more path components together and return the resulting path.
os.path.normcase(path): Normalize a pathname.
os.path.normpath(path):from collections.abc import Generator, Iterable, Iterator
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import attr
import attr.validators as validators
import jinja2.exceptions
from attr.converters import optional
from attrs_strict import StrictAttrs, field
from cached_property import cached_property
from flit_core.buildapi import get_cpython_version
from jinja2 import TemplateError
from mypy_extensions import Arg, KwArg, VarArg
from pydantic import BaseModel as PydanticBaseModel
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass
from rich.console import Console
from rich.syntax import Syntax
from toolz.curried import compose_left


if TYPE_CHECKING:
    from mypy_extensions import NamedArg
else:
    class NamedArg(Generic[NamedArg]):...


def _get_callable_name(func):
    """Return the name of a callable."""
    # https://github.com/python/cpython/blob/3.8/Lib/inspect.py#L1975-L1986
    if hasattr(func, '__qualname__'):
        return func.__qualname__.split('.')[0]
    elif hasattr(func, 'im_func') and getattr(func.im_class, '__module__', None) == '__builtin__':
        return func.im_func.__name__
    else:
        # https://github.com/python/cpython/blob/3.8/Lib/inspect.py#L1990-L1991
        return func.__name__

# TODO: refactor this into its own project/package?
@dataclass(frozen=True)
class CallableInfo:
    """
    Dataclass for storing information about a callable.

    Attributes:
    - name: The name of the callable.
    - module: The module where the callable is defined.
    - docstring: A brief description of the callable's purpose.
    - signature: A representation of the callable's parameters using inspect.signature().
    - source_code: The actual source code of the callable.

    Args:
    - func: The callable object for which information should be collected. This can be either a native function, a lambda expression, or any other callable that supports `__code__` attribute.
    """

    name: str = ''
    module: str | None = None
    docstring: str | None = None
    signature: inspect.Signature | None = None
    source_code: str | None = None

    def __post_init__(self):
        self.name = _get_callable_name(self.func)


# TODO: refactor this into its own project/package?
def extract_call_info_from_function