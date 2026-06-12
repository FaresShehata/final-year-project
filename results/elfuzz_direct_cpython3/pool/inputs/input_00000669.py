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
import collections.abc as abc
import contextlib
import functools
import glob
import itertools
import locale
import os
import re
import shutil
import sys
import time
import tokenize
import unicodedata
import warnings
from argparse import ArgumentParser, Namespace
from datetime import date, datetime, timedelta
from enum import Enum
from fractions import Fraction
from inspect import isfunction
from io import StringIO
from multiprocessing.spawn import freeze_support
from pathlib import Path
from pickle import loads, dumps
from pprint import pformat
from queue import Queue
from types import ModuleType
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    Generic,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    TypedDict,
    Union,
    cast,
)
from urllib.parse import urlparse
from weakref import ref

# These are all the modules that will be imported.
#
# If you change these paths, update the imports in seed01.py and seed02.py too.
#
# This should also include any other files that have @requires() decorators.
REQUIRES = {
    "asyncio": "unittest",
}

# Seed 03 — Arithmetic operations, Random number generators, math.pi
PI = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679
E = 2.71828182845904523536028747135266249775724709369995957496696762772407663035354


def pi_e_parser(
    parser: ArgumentParser, namespace: Namespace, values: Sequence[Any], option_string: str
) -> None:
    """
    Parse command-line arguments for PI_E.

    :param parser: The argument parser    },
    total=False,
)


def typed_dict_constraint(typeddict: Type[T]) -> Callable[[Type[T]], Type[T]]:
    """Decorator that adds an `__annotations__` attribute to the given type.

    Note this works by creating proxies of the given type which store a copy of its
    annotations. When it's called on a class, it checks if the given type has
