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
import random
import re
import shutil
import signal
import string
import subprocess
import sys
import traceback
import types
import unittest
import weakref
import collections.abc as abc
import collections
import contextlib
import copyreg
import functools
import hashlib
import itertools
import logging
import multiprocessing
import multiprocessing.connection
import multiprocessing.managers
import multiprocessing.pool
import multiprocessing.shared_memory
import operator
import queue
import reprlib
import runpy
import select
import shlex
import site
import socket
import sqlite3
import stringprep
import tempfile
import threading
import time
import tokenize
import typing
import warnings
import zlib


def main():
    print('Hello World!')


if __name__ == '__main__':
    main()


class Seed_01:
    """Seed 01 — Basic data structures, list comprehensions and generator expressions"""


# List comprehension
mylist = [x for x in range(10)]

# Generator expression
genexpr = (x for x in mylist)


class Seed_02:
    """Seed 02 — String formatting, f-strings, bytes literals, hexdumping"""


# String formatting
print("My name is %s" % "John")

# F-Strings
person_name = 'Doe'
print(f"My name is {person_name}")

# Bytes literal
byte_literal = b'Hello'

# Hexdumping
data_bytes = b'\x01\x02\xff'
hex_dump = ''.join([f'{byte:02X}' for byte in data_bytes])
print(hex_dump)

# Binary operators
result = 5 + 7 * 8 / 2 - 9 // 3 ** 2
print(result)  # Output: 16

# Bitwise operators
a = 10
b = 5
print(a & b)  # Output: 0
print(a | b)  # Output: 15
print(~a)     # Output: -11
print(a ^ b)  # Output: 15
print(a << 2)  # Output: 40
print(a >> 2)  # Output: 2

# String methods
text = "hello world"
uppercase_text = text.upper()
reversed_text = text[::-1]
count_of_a = text.count('a')

# String formatting with str.format()
