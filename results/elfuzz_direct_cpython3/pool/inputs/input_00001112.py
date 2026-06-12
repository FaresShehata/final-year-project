"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets,
          stringio
"""

from typing import (
    Tuple, Iterable, Optional, Sequence,
    Callable, Awaitable, Generator, Union,
    Any, Literal,
    Protocol, ClassVar, TYPE_CHECKING, runtime_checkable,
    NoReturn, TypedDict, ParamSpec, Concatenate, TypeAlias,
    Never, Annotated, get_type_hints, reveal_type
)

import sys
import os
import re
import subprocess
import time
import asyncio
import functools
import inspect
import ast
import tokenize
import io
import string
import collections.abc
import itertools
import zipfile
import traceback
import importlib.util
import random
import math
import textwrap
import texttable

import collections
import contextvars
import enum
import abc
import dataclasses
import pickle
import types

import numpy as np
import pandas as pd
import pandas.core.indexes.api as pdi
import scipy.sparse
import sympy
import networkx as nx
import pygraphviz as pgv
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn.datasets
import sklearn.linear_model
import sklearn.model_selection
import sklearn.pipeline
import sklearn.preprocessing
import sklearn.svm
import sklearn.discriminant_analysis
import sklearn.tree
import sklearn.naive_bayes
import sklearn.neighbors
import sklearn.neural_network
import sklearn.decomposition
import sklearn.feature_extraction.text
import sklearn.metrics
import sklearn.pipeline
import sklearn.preprocessing
import sklearn.utils._testing
import sklearn.utils.validation
import sklearn.compose
import sklearn.impute
import sklearn.base
import sklearn.gaussian_process
import sklearn.kernel_ridge
import sklearn.svm.classes
import sklearn.multiclass
import sklearn.ensemble
import sklearn.linear_model
import sklearn.naive_bayes
import sklearn.tree
import sklearn.pipeline
import sklearn.preprocessing
import sklearn.utils._testing
import sklearn.utils.validation
import sklearn.compose
import sklearn.impute
import sklearn.base
import sklearn.gaussian_process
import sklearn.kernel_ridge
import sklearn.svm.classes
import sklearn.multiclass
import sklearn.ensemble
import sklearn.linear_model
import sklearn.naive_bayes
import sklearn.tree
import sklearn.pipeline
import sklearn.preprocessing
import sklearn.utils._testing
import sklearn.utils.validation
import sklearn.compose
import sklearn.impute
import sklearn.base
import sklearn.gaussian_process
import sklearn.kernel_ridge
import sklearn.svm.classes
import sklearn.multiclass
import sklearn.ensemble
NOT   = lambda p: p(FALSE)(TRUE)

ZERO  = lambda f: lambda x: x
SUCC  = lambda n: lambda f: lambda x: f(n(f)(x))
ADD   = lambda m: lambda n: lambda f: lambda x: m(f)(n(f)(x))
MUL   = lambda m: lambda n: lambda f: n(m(f))
ONE   = SUCC(ZERO)
TWO   = SUCC(ONE)
THREE = SUCC(TWO)

def church_to_int(n) -> int:
    return n(lambda x: x + 1)(0)

def int_to_church(n: int):
    result = ZERO
    for _ in range(n):
        result = SUCC(result)
    return result


# ── Currying & partial application ───────────────────────────────────────────

def curry(fn: Callable) -> Callable:
    """Auto-curry a function based on its arity."""
    arity = fn.__code__.co_argcount

    @functools.wraps(fn)
    def curried(*args):
        if len(args) >= arity:
            return fn(*args[:arity])
        return lambda *more: curried(*(args + more))

    return curried


@curry
def add3(a: int, b: int, c: int) -> int:
    return a + b + c


add3 = add3.currier() # same as `add3` but auto-curried when called with fewer than three arguments

add4 = curry(int.__add__)


# ── Partial application ─────────────────────────────────────────────────────

def partial(func: Callable[[A], B], /, *args: A) -> Callable[..., B]:
    """Returns a partially-applied function of the given func."""
    
    @functools.wraps(func)
    def wrapper(*psb_args: B):
        args = (*args, *psb_args)
        return func(*args)

    return wrapper



# ── Trampolining ───────────────────────────────────────────────────────────

class TrampolineError(Exception): pass

def trampoline_aware_caller(callable_, /, *args):
    try:
        result = callable_(*args)
    except ValueError:
        raise TrampolineError from None
    while isinstance(result, Callable):
        try:
            result = result()
        except TrampolineError:
            break
    else:
        return result

trampoline_aware_call = functools.partial(trampoline_aware_caller)


def trampoline(coro: Coroutine[Any, Any, T]) -> T:
    """Trampoline implementation."""

    async def wrapper():
        while True:
            try:
                yield await coro.__anext__()
            except StopAsyncIteration as e:
                return e.value
    
    return trampoline_aware_call(wrapper().__aiter__(), __await__)