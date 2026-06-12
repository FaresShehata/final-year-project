"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""
import ast
from collections import Counter
from datetime import date, timedelta
from enum import Enum
from io import StringIO
from itertools import count
import logging
import os
import re
import sys
import types
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
)
import tokenize
import time
import textwrap
import warnings

from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
import inspect
from paramiko.ssh_exception import SSHException
from pathlib import Path
import pprint
from types import ModuleType
from typing_extensions import Literal, TypedDict


# You can also use 'typing' for more advanced type declarations.
# For example, if you want to declare a class that is only used in the module where it's defined:
#
# from typing import Self
#
# def self_reference(self) -> Self:
#     return self
#
# Then you could do something like this:
#
# from self_example import self_reference
#
# print(self_reference()) # This should be an instance of self_example.self_reference.


def _get_args(func):
    """Get the positional arguments of a function."""
    signature = inspect.signature(func)

    args = []
    for name, param in signature.parameters.items():
        if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.KEYWORD_ONLY:
            args.append(name)

    return tuple(args)


def _get_kwargs(func):
    """Get the keyword-only arguments of a function."""
    signature = inspect.signature(func)

    kwargs = {}
    for name, param in signature.parameters.items():
        if param.kind != param.POSITIONAL_OR_KEYWORD and param.kind != param.VAR_POSITIONAL:
            kwargs[name] = param.default

    return kwargs


def _make_signature(function, *, positionals=None, keywords=None, defaults=None):
    """Make a Signature object based on the given function."""

    return inspect.Signature(
        parameters=[
            Parameter(name=name, kind=Parameter.POSITIONAL_OR_KEYWORD, default=default)
            for name, default in (defaults or {}).items()
        ]
        + [
            Parameter(
                name=param.name,
                kind=getattr(param.kind, "value", param.kind),
            )
            for param in signature.parameters.values()
            if positionals is None or param._name in positionals
            or (
                keywords is not None
