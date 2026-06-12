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
import operator
import os
import pickle
import platform
import queue
import re
import random
import string
import sys
import traceback
import types
import typing as t

import memoryview
import pathlib
import pprint
import reprlib
import signal
import sqlite3
import subprocess
import sysconfig
import tempfile
import threading
import time
import traceback
import warnings
import weakref


class Foo:
    def __init__(self, a):
        self.a = a
        print("Foo.__init__()")

    @classmethod
    def class_method(cls):
        pass

    def instance_method(self):
        print(f"Foo.instance_method({self})")

    def method_with_default_param(a=1):
        return a + 1

    def method_with_star_args(*args):
        return args

    def method_with_double_star_kwargs(**kwargs):
        return kwargs

    def method_with_all_params(
            a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None, i=None, j=None, k=None
    ):
        return (a, b, c, d, e, f, g, h, i, j, k)

    def method_with_variadic_args_and_keywords_unpacking(
            *args, **kwargs):
        return (args, kwargs)

    def method_with_positional_only_args_and_keywords(
            /, *, a=None, b=None, c=None, d=None, e=None, f=None, g=None, h=None, i=None, j=None, k=None):
        return (a, b, c, d, e, f, g, h, i, j, k)


def function_without_name():
    pass


# Seed 05

if False:
    # Seed 06 - Exception handling and assertions
    # Seed 07 - Error handling with try-except-finally blocks
    # Seed 08 - Errors with raise statements
    # Seed 09 - Custom exceptions
    # Seed 10 - Debugging with pdb
    pass


def seed_11_exception_handling() -> None:
    """Exception handling and assertions"""

    def divide(num1: int, num2: int) -> int:
        if num2 == 0:
            raise ZeroDivisionError('num2 cannot be zero')
        else:
            return num1 // num2