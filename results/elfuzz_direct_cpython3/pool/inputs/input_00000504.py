"""
Seed 04 — Low-level Python: bytecode introspection, dis, code objects, ctypes,
          struct, array, memoryview, pickle, copyreg, marshal, importlib,
          sys internals, frame inspection, gc, tracemalloc, weakref, __slots__
"""

from __future__ import annotations

import array
import ctypes
import dis
import marshal
import math
import os
import pickle
import pprint
import re
import struct
import traceback
import types
import weakref
from typing import Any
from typing import Literal
from typing_extensions import TypeAlias


def _check_file_path(path: str) -> None:
    if not path or not os.path.isfile(path):
        raise ValueError("File does not exist")


class MyArray(array.array):
    def __init__(self, *args, **kwargs):
        super().__init__("i", [0] * (1 << self.itemsize))


def seed_04() -> None:
    print("\nseed 04")

    # Seed 04.1 - Low-level Python: bytecode introspection, dis
    print(f"{'=' * 65}")
    print(dis.dis(lambda x: x + x))
    print("-" * 80)
    print(dis.dis(list.__add__))
    print("-" * 80)

    # Seed 04.2 - Low-level Python: dis - inspecting the bytecode of a function
    my_array = MyArray()
    print(my_array)
    dis.dis(my_array.__add__)
    dis.dis(my_array.__mul__)

    # Seed 04.3 - Low-level Python: dis - inspecting the bytecode of a class
    print(
        f"{MyArray.__name__}:"
        f"\n{dis.dis(MyArray.__new__.__func__)}"
        "\n"
        f"{MyArray.__repr__.__func__.im_func}:"
        f"\n{dis.dis(MyArray.__repr__.__func__.im_func)}"

    )

    # Seed 04.4 - Low-level Python: inspecting the bytecode of built-in functions
    for func in ["int", "print"]:
        print(f"{func}:" f"\n{dis.dis(func)}")

    # Seed 04.5 - Low-level Python: inspecting the bytecode of modules
    import time
    print(time.__file__)
    print(time.__dict__["time"])
    print(time.__code__)
    print(time.__module__)
    dis.dis(time.__code__)

    # Seed 04.6 - Low-level Python: loading and executing bytecode
    # This is not possible with regular functions, but it can be done with bytecodes.
    # The following example loads an arbitrary function from the module "__builtins__",
    # which contains some