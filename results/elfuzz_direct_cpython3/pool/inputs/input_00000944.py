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
import marshal
import math
import os
import pickle
import platform
import re
import sys
import traceback
import types
import typing
import weakref
from datetime import datetime as dt
from inspect import isclass, getmembers, getsource, getdoc, stack, getfullargspec, signature, getmodule, CO_GENERATOR, Signature, Parameter
from pathlib import Path
from pickletools import simple_decompile
from pprint import pprint
from random import randint
from timeit import default_timer as timer
from types import CodeType
from typing import TypeVar, Union, Sequence, Any, Tuple, Iterable, Callable, List, overload, Optional, Dict, Set, FrozenSet, MutableSequence, Literal
from warnings import warn

print(f"Python version {sys.version}")
print(f"Platform: {platform.system()}")
print(f"Machine architecture: {platform.machine()}")
print(f"Operating system: {platform.system().lower()}")

# Seed 01 - Basic data structures, literals and expressions (numbers, strings, lists, sets, dicts)
# Numbers
print("Numbers")
a = 3.0 ** 2 + 5 / 7 * 6 % 8 // 9
b = -(math.pi)
c = complex(3, 4)
d = int(b)
e = float(c.real)
f = c.imaginary()
g = bool(a)
h = bin(g)
i = oct(h)
j = hex(i)
k = chr(j)

print(type(a), a, type(b), b, type(c), c, type(d), d, type(e), e, type(f), f, type(g), g, type(h), h, type(i), i, type(j), j, type(k), k, sep="\n")

# Strings
print("Strings")
str_1 = 'Hello'
str_2 = "World"
str_3 = """
This
is
multiline
string.
"""

print(str_1, str_2, str_3, sep="\n", end="...\n")

# Lists
print("Lists")
list_1 = [1, 2, 3]
list_2 = [4, 5, 6]
list_3 = list_1 + list_2
list_4 = ["A", "B", "C"]
list_5 = [7, 8, 9]
list_6