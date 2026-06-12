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
import gc
import inspect
import importlib as imp
import itertools
import os
import pickle
import platform
import pprint
import re
import signal
import socket
import sys
import time
import types
import tracemalloc
import typing as t
import uuid
import _thread as thread

if hasattr(thread, "_local"):
    from threading import Lock as ThreadLocalLock
else:
    class ThreadLocalLock(object):
        def __init__(self):
            self.lock = threading.Lock()
            self.release_count = 0

        def acquire(self, blocking=True, timeout=None):
            if self.release_count == 0:
                self.lock.acquire(blocking, timeout)
            else:
                self.release_count += 1

        def release(self):
            self.release_count -= 1
            if self.release_count <= 0:
                self.lock.release()

        def locked(self):
            return self.locked_locked or self.release_count < 0

        def set_lock(self, lock):
            self.lock = lock

        def __enter__(self):
            self.acquire()

        def __exit__(self, exc_type, exc_value, traceback):
            self.release()


class UUID(t.TypedDict):
    """A UUID object."""

    data: bytes


# ── Python internals ──────────────────────────────────────────────────────────

def get_current_frame(depth: int = 1) -> types.FrameType | None:
    """
    Return the current frame.

    The depth parameter specifies how many frames above the current one to go.
    For example, depth=1 will return the frame that called this function.
    """
    try:
        return sys._getframe(depth).f_back    # type: ignore[attr-defined]
    except ValueError:
        print(f"No frame at {depth} levels up.")
        return None


def frame_info_func(func: types.FunctionType) -> tuple[str, ...]:
    """Return the arguments and the locals dictionary associated with func."""
    f_locals = func.__code__.co_varnames
    args = [arg for arg in inspect.getfullargspec(func)[0]]
    new_args = []
    for i, (name, value) in enumerate(zip(args, list(locals().values()))):
        if name not in f_locals[:i + 1] and name != "self":
            new_args.append(name)

    return new_args, frozenset(new_args)


def walk_frames(frame: types.TracebackType, context_ufuncs: dict[UUID, str]) -> None:
    """Walk the stack until we reach a UFunc."""
    while True:
        lineno = frame.f_lineno - 1
        co = frame.f_code
        filename = co.co_filename
        name = co.co_name
        linecache.checkcache(filename)  # type: ignore[arg-type]

        source_lines, start_line_no = linecache.getlines(
            filename,
            module_globals=frame.f_globals,
            cache=context_ufuncs,
        )
        start_line_no -= 1
        end_line_no = len(source_lines) - 1
        try:
            start_line_no = next(i for i, line in enumerate(source_lines[start_line_no:])
                                 if line.strip() == f"# @ {name}")
        except StopIteration:
            pass

        end_line_no = min(end_line_no, start_line_no + 256)
        lines = "\n".join(
            source_lines[i * 8 : (i + 1) * 8] for i in range((end_line_no - start_line_no) // 8 + 1),
        )

        yield (filename, lineno, name, lines), start_line_no, end_line_no

        try:
            frame = frame.f_back
            if frame is None:
                break
        except AttributeError:
            break


def call_a_function(obj: object, attr: str, *args: object, **kwargs: object) -> object:
    """Call an attribute of obj with args and kwargs."""
    try:
        method = getattr(obj, attr)
    except AttributeError:
        raise AttributeError(f"{obj} has no attribute {attr}")

    if isinstance(method, types.MethodType):
        method = method.__func__

    return method(*args, **kwargs)


def make_a_class(class_name: str, bases: tuple[type], attributes: dict[str, object]) -> type:
    """