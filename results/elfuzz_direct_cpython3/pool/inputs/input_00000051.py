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
import io
import marshal
import os
import pprint
import pickle
import platform
import re
import reprlib
import shutil
import subprocess
import struct
import sys
import tracemalloc
import traceback
import types
import typing as tp
import unittest.mock
import warnings
import weakref


# ── misc ─────────────────────────────────────────────────────────────────────

def get_sys_info() -> str:
    """
    Print some system information about the current running process.
    """
    with open("/proc/%s/status" % os.getpid(), "rb") as f:
        status = f.readlines()
    data = {}
    for line in status:
        if not line.startswith(b"\n"):
            key, value = line.split(b":")
            key = key.strip().decode()
            value = value.strip().decode()
            try:
                value = int(value)
            except ValueError:
                pass
            data[key] = value
    return pprint.pformat(data).replace("'", '"')


def set_trace() -> None:
    """Use pdb.set_trace() to start debugging."""
    import pdb; pdb.Pdb(stdout=sys.stdout).set_trace(sys._getframe())


def test_pdb() -> None:
    import random
    from itertools import islice

    def rng():
        while True:
            yield random.randint(0, 5)

    def primes(n):
        return filter(isprime, rng())

    def isprime(x):
        for i in range(3, int(x**0.5) + 1, 2):
            if x % i == 0:
                return False
        return True

    print(list(islice(primes(100), 20)))

    import pdb
    pdb.set_trace()


# ── run tests ────────────────────────────────────────────────────────────────

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmpdir = tempfile.mkdtemp()

    def setUp(self) -> None:
        self.tmpfile = tempfile.NamedTemporaryFile(dir=self._tmpdir)

    def tearDown(self) -> None:
        self.tmpfile.close()
        shutil.rmtree(self._tmpdir)

    def test_undefined_variable(self) -> None:
        """Test that undefined names are handled gracefully."""
        exec('print(undefined)', {})


# ── code object ──────────────────────────────────────────────────────────────

def compile_code(code: str, filename: str) ->    flat = [coord for p in points for coord in p]
    return struct.pack(fmt, *flat)


# ── array & memoryview ────────────────────────────────────────────────────────

def array_ops() -> dict:
    a = array.array("d", range(10))            # double array
    b = array.array("d", [x ** 2 for x in a])

