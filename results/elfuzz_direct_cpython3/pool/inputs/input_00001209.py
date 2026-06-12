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
    print("Hello World!")

# Integer literals
int_10 = 10   # Decimal
int_16 = 0xA  # Hexadecimal
int_8 = 0o10  # Octal
int_2 = 0B10  # Binary

# Floating point literals
float_value = 3.14

# Complex number literals
complex_number = 2j

# Boolean literals
is_true = True
is_false = False

# None literal
none_value = None

# String literal
string_literal = "This is a string"

# Byte literal
byte_literal = b'This is a byte'

# Raw string literal (no escape sequences)
raw_string_literal = r'This \n is a raw string'

# Multiline string literal (triple quotes)
multiline_string = '''This is a multiline
string'''

# Concatenation and repetition of strings
concat_string = 'Hello ' + 'World'
multiplied_string = 'spam' * 3

# String methods
uppercase_string = string_literal.upper()

# String formatting with f-strings
name = "Alice"
print(f"Hi, {name}!")

# String slicing
substring = string_literal[6:]
subslice = substring[:3]

# String indexing
first_char = string_literal[0]  # 'H'

# String length
length = len(string_literal)

# String concatenation
another_string = " Hello"
final_string = string_literal + another_string

# String comparison
if string_literal == "Hello":
    print("It's the same string")

# String membership test
contains_substring = "world" in string_literal

# String iteration
for char in string_literal:
    print(char)


# Type conversions
int_to_float = float(10)
str_to_bool = bool("True")
bool_to_int = int(True)

# String methods
lower_case = string_literal.lower()
upper_case = string_literal.upper()
capitalize = string_literal.capitalize()


# String format method
formatted_string = "{}, {}!".format("Hello", "World")


# Escape characters
escaped_backslash = "This is a backslash \\."
escaped_quote = 'This is a single quote \'.'

# String methods for removing whitespaces
trim_whitespace = "   Whitespace   ".strip()  # Removes leading/trailing whitespace
replace_whitespace = "Whitespace".replace(" ", "-")  # Replaces all occurrences of whitespace character



# Advanced string methods
leftprint(f"My name is {person_name}")

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
