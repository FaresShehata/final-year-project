"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import functools
import gc
import inspect
import importlib.util
import itertools
import math
import os
import platform
import random
import re
import shutil
import string
import sys
import traceback
import types
import typing as t
import warnings
import weakref

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pydantic
import scikit_posthocs as sp
import scipy.stats as stats
import seaborn as sns
import sympy
import tabulate
import tqdm.notebook
import yaml
from matplotlib.colors import LinearSegmentedColormap


def seed(seed_num: int | None = None) -> None:
    """
    Set the global random state for reproducibility.

    Args:
        seed_num (int): Seed number to use.
            If ``None``, will use the current timestamp.

    """

    if seed_num is None:
        seed_num = int(str(int(os.getpid())) + str(random.randint(1, 9)))

    # For reproducible results with NumPy and other libraries that are seeded by the CPython interpreter
    random.seed(seed_num)
    np.random.seed(seed_num)

    return None


seed()

# --------------------------------------------------- #
#           2. Low-Level Python - Bytecode             #
# --------------------------------------------------- #

class Foo:
    def bar(self):
        ...


foo_obj = Foo()

print(f"Foo.__dict__: {Foo.__dict__}")
print(f"Foo.bar:     {Foo.bar}")

for key in dir(foo_obj):
    print(key)

print(dir(Foo))
print([key for key in dir(Foo)])

print(type(Foo))

# --------------------------------------------------- #
#       3. Low-Level Python - Disassembly              #
# --------------------------------------------------- #

dis_module = "bar"
dis_source_code = f"""\
{dis_module}:"""
exec(dis_source_code)
dis_func = getattr(sys.modules[dis_module], dis_module)


print(inspect.getsource(dis_func))
print("Disassembled:", end=" ")
print(repr(dis_func))


bytecode_lines = [f"{line.opname:16}: {line.oparg}" for line in dis_func.dis()]
print("\n".join(bytecode_lines))

print("Bytecodes:")
for i, op in enumerate(dis_func.code.co_code):
    print(f"{i}. {op:02x}")


print("=" * 80)
print("=" *