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
import pickle
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tokenize
import traceback
import unittest.mock as mock
import weakref
from collections.abc import Callable, Hashable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from html.parser import HTMLParser
from inspect import Parameter, signature
from itertools import chain
from logging import Logger
from math import isclose, log10
from operator import add, mul
from pathlib import Path
from queue import Queue
from tempfile import NamedTemporaryFile, TemporaryDirectory
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Final,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)
from urllib.parse import quote_plus
from uuid import UUID
from warnings import warn

# TODO: https://peps.python.org/pep-0672/#convention-over-configuration
from _pytask.config import hookimpl


def decorator(*args, **kwargs):
    """
    Decorator for printing the function name and location.

    Parameters
    ----------
    *args :
        Positional arguments passed to the decorated function.
    **kwargs :
        Keyword arguments passed to the decorated function.

    Returns
    -------
    Function
        The wrapper function that prints the function name and location.
    """

    def wrapper(func):
        @wraps(func)
        def wrapped_func(*f_args, **f_kwargs):
            print(f"Calling {func.__name__} from {func.__code__.co_filename}")
            return func(*f_args, **f_kwargs)

        return wrapped_func

    if len(args) == 1 and callable(args[0]):
        # No arguments are provided. Return a new function that will be used as a decorator.
        return wrapper(args[0])
    else:
        # One or more arguments are provided. Return the decorated function directly.
        return wrapper


@decorator
def my_decorator(func):
    """Simple example of using Python decorators."""

    print("Running my decorator.")

    def wrapper(*args, **kwargs):
        print("Before calling %s." % func.__name__)
        value = func