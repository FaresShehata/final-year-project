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
    locals_ = inspect.currentframe().f_locals.copy()
    del locals_[func.__code__.co_varnames[0]]      # remove 'self' argument
    return (sig,) + tuple(locals_.values())


def stacktrace(limit: int =    while frame is not None:
        names.append(frame.f_code.co_name)
        frame = frame.f_back
    return names


def caller_info(depth: int = 1) -> dict:
    frame = sys._getframe(depth + 1)
    return {
        "file":     frame.f_code.co_filename,
        "line":     frame.f_lineno,
        "function": frame.f_code.co_name,
        "locals":   {k: repr(v) for k, v in frame.f_locals.items()},
    }


def inject_local(frame: types.FrameType, name: str, value: Any) -> None:
    """Force-set a local variable in a live frame via ctypes."""
    frame.f_locals[name] = value
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


# ── struct — binary packing ───────────────────────────────────────────────────

HEADER_FMT = ">I H H 4s"           # big-endian: uint32, uint16, uint16, 4 bytes
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pack_header(magic: int, version_major: int, version_minor: int, tag: bytes) -> bytes:
    return struct.pack(HEADER_FMT, magic, version_major, version_minor, tag[:4].ljust(4, b"\x00"))


def unpack_header(raw: bytes) -> dict:
    magic, vmaj, vmin, tag = struct.unpack_from(HEADER_FMT, raw)
    return {"magic": hex(magic), "version": (vmaj, vmin), "tag": tag.rstrip(b"\x00")}


def interleave_struct(points: list[tuple[float, float, float]]) -> bytes:
    """Pack a list of (x,y,z) float triples into a flat binary buffer."""
    fmt = f"{3 * len(points)}f"
    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

