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
    args, _, _, defaults = inspect.getargspec(func)
    sig_str = ", ".join(args[-len(defaults):])    # omit positional default values
    sig = f"{func.__module__}.{func.__name__}({sig_str})"
    var_names = list(inspect.signature(func).parameters.keys())
    return (sig,) + tuple(var_names)


def frame_with_args(frame: types.FrameType, args: dict[str, t.Any], **kwargs: t.Any) -> types.FrameType:
    """Create a new frame with the given arguments and keyword arguments."""
    for arg_name in kwargs:
        assert arg_name not in frame.f_globals, (
            f"Error when creating a new frame: "
            "the argument name '{arg_name}' is already present in the globals of the parent scope."
        )
    local_vars = {
        *frame.f_locals.items(),
        *((arg_name, value) for arg_name, value in args.items()),
        *(key, value) for key, value in kwargs.items()
    }
    return types.FrameType(
        frame.f_code.co_consts,
        frame.f_code.co_filename,
        frame.f_code.co_firstlineno,
        frame.f_code.co_lnotab,
        frame.f_code.co_names,
        frame.f_code.co_varnames,
        frame.f_trace,
        frame.f_lineno,
        frame.f_globals.copy(),
        local_vars,
        frame.f_builtins
    )


def frame_info() -> str:
    """Get information about the current frame."""
    frame = sys._getframe(1)   # type: ignore[attr-defined]
    # frame.pycode.name = "<string>"
    info = [f"<{frame.f_code.co_filename}:{frame.f_lineno}>"]
    vars_ = frame.f_locals.copy()
    vars_.update(dict(zip(frame.f_code.co_varnames, frame.f_code.co_varnames)))
    lines = []
    while True:
        line = frame.f_code.co_code[frame.f_lasti:]
        frame.f_lasti += len(line)
        try:
            op = dis.opmap[dis.opname[dis.opvalue(line)]]
            opcode = op >> 8
            if opcode >= 172:
                break
            lines.append(dis.opname[op])
        except KeyError:
            break
    info.extend(lines)
    info.append(pprint.pformat(vars_, indent=4))
    return "\n".join(info)


FRAME_INFO_FUNC_CACHE: dict[type[types.FunctionType], dict[str, list[tuple[str, ...]]]] \
                   | None = None

@lru_cache(maxsize=None)
def frame_info_func_cached(func: types.FunctionType) -> dict[str, list[tuple[str, ...]]]:
    global FRAME_INFO_FUNC_CACHE
    if FRAME_INFO_FUNC_CACHE is None:
        FRAME_INFO_FUNC_CACHE = {}
    cached_data = FRAME_INFO_FUNC_CACHE.get(type(func), None)
    if cached_data is None:
        cached_data = FRAME_INFO_FUNC_CACHE[type(func)] = {}
    cached_funcs = cached_data.get(func, [])
    if func not in cached_funcs:
        cached_funcs.append(func)
        cached_data[func] = cached_funcs
    return {f"{func.__module__}.{func.__name__}": frame_info_func(func)}


def frame_info_cached() -> str:
    funcs = sys._getframe().f_locals.copy()     # type: ignore[attr-defined]
    funcs.update(sys._getframe().f_globals.copy())       # type: ignore[attr-defined]
    for func in funcs.values():
        if isinstance(func, types.FunctionType):
            break
    else:
        return ""
    return pprint.pformat(frame_info_func_cached(func))


def check_file_exists(filename: str) -> bool:
    """Check if the file exists on disk."""
   