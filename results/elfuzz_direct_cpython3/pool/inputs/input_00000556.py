"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import collections.abc as cabc
import functools
import inspect
import itertools
import logging
import operator
import os
import pathlib
import pprint
import re
import types
import typing
import warnings

import importlib.resources
import numpy.typing as npt
import pkg_resources
import pycodestyle
import pytest
import pytypest.main
import sysconfig
import textwrap
import traceback
import tokenize
import typing_extensions
import weakref
import xml.etree.ElementTree


def test_mypy():
    """test-mypy.py"""

    from mypy import api

    errors = api.run(["-c", "print('hello')"])
    assert errors == ("No issues found in file\n", None)


def test_cython():
    """cython.pyx"""

    from cython.test.cython_test import TestCython

    t = TestCython()
    print(t.add(3, 5))
    # 8


def test_tracemalloc():
    """tracemalloc.py"""

    import tracemalloc

    tracemalloc.start()

    for i in range(10_000):
        pass

    snapshot = tracemalloc.take_snapshot()

    top_stats = snapshot.statistics("lineno")

    print(f"{len(top_stats)} Top Resource Contenders:")

    for stat in top_stats[:5]:
        print(stat)

    with open(os.devnull) as devnull:
        result = subprocess.run(
            ["python", "-m", "trace", "--show-backups"],
            stdin=devnull,
            stdout=subprocess.PIPE,
        )

    print(result.stdout.decode())


def test_gc():
    """gc.py"""

    import gc

    class A:
        pass

    a = [A() for _ in range(10)]
    b = []
    b.append(a[0])
    del a
    print(gc.collect())  # 1
    print(len(b))  # 1
    print(gc.collect())  # 1
    print(len(b))  # still 1


def test_struct_xml():
    """
    https://docs.python.org/3/library/xml.html#xml-module-structuring-and-parsing-trees

    https://docs.python.org/3/library/xml.html#xml-tree-structuring-and-parsing-trees

    https://stackoverflow.com/a/62575991
    """

    import xml.etree.ElementTree as    )


# ────────────────────────────────────────────────────────────────────────────


class AbstractClassA(metaclass=RegistryMeta):
    pass


@functools.total_ordering
class ConcreteClassA(AbstractClassA):
    x: int


class AbstractClassB(metaclass=RegistryMeta):
    y: int


@functools.total_ordering
class ConcreteClassB(AbstractClassB):
    y: int

    @property
    def z(self):
        return self.y * 2


if __name__ == "__main__":
    assert len(RegistryMeta._registry["AbstractClassB"]) == 1
    print(*sorted(RegistryMeta._registry.values()), sep="\n")
    # ConcreteClassB