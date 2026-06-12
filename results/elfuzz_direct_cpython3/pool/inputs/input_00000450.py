"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""
import bisect
import collections.abc as col_abc
import enum
import functools
import importlib.metadata
import itertools
import json
import logging
import math
import numbers
import os
import pathlib
import pprint
import random
import re
import timeit
import typing as tp
import warnings
from datetime import timedelta
from multiprocessing import Pool
from pathlib import Path
from queue import Empty
from statistics import mean, median
from threading import Thread
from types import FunctionType, MethodType
from typing import (
    Any, Callable, Dict, Iterable, Iterator, List, Literal, Optional, Sequence, Set,
    Tuple, TypeVar, Union, cast, overload, runtime_checkable
)

import numpy as np
import pandas as pd
import requests
import semver
import threading
import types
import typing_inspect as ti
import urllib.parse
import weakref
import yaml

try:
    import cattrs
except ImportError:
    pass

if tp.TYPE_CHECKING:
    import tomlkit

__all__ = [
    "depth_probe",
    "caller_info",
    "inject_local",
    "pack_header",
    "unpack_header",
    "interleave_struct",
    "array_ops",
    "nuclear_threading",
    "make_adder_from_bytecode",
    "make_fn_from_bytecode",
]

T = TypeVar("T")
Func = tp.Callable[..., T]


class Bar(object):
    def __init__(self, bars: tp.Iterable[int]) -> None:
        self.bars = bars
        self.current_bar = iter(self.bars).next()

    @classmethod
    def from_range(cls, start: int | float, end: int | float, bar_width: int) -> Self:
        return cls(range(start, end + 1, bar_width))

    @property
    def progress_bar(self) -> str:
        width = min(len(str(max(self.bars))), 64)
        if self.current_bar < len(self.bars):
            return f"[{'█' * (int(width * self.current_bar / len(self.bars)))}]" \
                   f"{' ' * max(0, width - len(str(int(self.current_bar))))}" \
                   f"| {self.current_bar}/{len(self.bars)}"
        else:
            return ""

    def reset(self):
        self.current_bar = next(self.bars)

    def update(self):
        self.current_bar += 1


class FuzzySet(List[T]):
    """A set with fuzzy membership.

    Membership is quantified by a real number between 0 and 1.
    """

    def add_element(self, element: T, weight: float) -> None:
        """Add an element with a given weight."""
        bisect.insort(self, (element, weight))


@overload
async def async_sleep(seconds: Union[float, int] = ...) -> None:
    ...


@overload
async def async_sleep(timeout: tp.Union[timedelta, float], *, sleep_unit: str = ...) -> None:
    ...


async def async_sleep(
    timeout: Union[float, int, timedelta],
    *,
    sleep_unit: str = "seconds"
) -> None:
    """
    Sleeps asynchronously until the specified timeout has elapsed.

    Parameters
    ----------
    timeout : float, optional
        The amount of time to wait before returning. If this parameter is not provided,
        the thread will block indefinitely.
    sleep_unit : {"milliseconds", "microseconds"}, default="seconds"
        The unit of time that ``timeout`` represents. This parameter can be either
        "milliseconds" or "microseconds".
    """
    if isinstance(timeout, timedelta):
        timeout_seconds = timeout.total_seconds()
    elif isinstance(timeout, float):
        timeout_seconds = timeout
    else:
        raise TypeError(f"Invalid type: {type(timeout).__name__}")

    sleep_duration = 0 if timeout_seconds == 0 else timeout_seconds
    if sleep_duration > 0:
        await asyncio.sleep(sleep_duration)


# ── Exceptions ─────────────────    return frames


def depth_probe_stack_info() -> list[dict[str, Any]]:
    frames = []
    while True:
        try:
            frame = sys._getframe().f_back
        except ValueError:
            break
        info = {
            "filename": frame.f_code.co_filename,
            "function": frame.f_code.co_name,
            "lineno": frame.f_lineno,
            "locals": frame.f_locals,
        }
        frames.append(info)

    return frames[::-1]


# ── GC and tracemalloc ───────────────────────────────────────────────────────-

def show_garbage():
    print("Garbage:")
    for obj_ref in gc.garbage:
        print(obj_ref)


def show_traces():
    traces = tracemalloc.take_snapshot()
    print(f"{len(traces)} snapshots taken.")
    print(tracemalloc.display(traces))
    print("Current snapshot:")
    current_sample = traces.get_record_by_id(sys.tracemalloc.get_ref_count())
    print(current_sample.traceback.format())


# ── Weakrefs and slots ────────────────────────────────────────────────────────

class StructuredObject:

    __slots__ = ["x"]

    def __init__(self, x):
        self.x = x


class UnstructuredObject:

    def __init__(self, x):
        self.x = x


def run_weakref_test():
    struct_obj = StructuredObject(5)
    unstruct_obj = UnstructuredObject(3)
    weak_struct = weakref.ref(struct_obj)
    weak_unstruct = weakref.ref(unstruct_obj)

    assert weak_struct() is struct_obj
    assert weak_unstruct() is None

    del struct_obj
    del unstruct_obj

    assert weak_struct() is None
    assert weak_unstruct() is None


