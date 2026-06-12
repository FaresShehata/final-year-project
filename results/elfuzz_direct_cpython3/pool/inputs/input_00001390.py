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
import inspect
import math
import os
import pprint
import random
import re
import shutil
import signal
import string
import subprocess
import sys
import traceback
import types
import typing as tp


def seed_04() -> None:
    """Low-level Python: bytecode introspection, dis, code objects, ctypes,
       struct, array, memoryview, pickle, copyreg, marshal, importlib,
       sys internals, frame inspection, gc, tracemalloc, weakref, __slots__

    """
    (1,) in []
    print(
        {i: i for i in range(10)}
    )  # dict comp with key and value being same expr; {key: val for val in iterable}
    print(type({i: i}))  # dict type
    print(set())  # empty set
    print(re.match(r"a\w*", "abacus"))  # match object of re module
    print(dis.dis("\n".join(["1", "2"])))  # list comp that's (1) a generator & (2) a comprehension
    print(eval("1 + 2"))  # evals the str passed to it
    print(bool([]))  # bool of any container that contains (empty) iterables will be False
    print(random.random())
    seed = int.from_bytes(os.urandom(3), byteorder="big") % 998244353
    print(seed)
    print(math.sqrt(seed))
    print(math.log10(seed))


if __name__ == "__main__":
    seed_04()

# EOF