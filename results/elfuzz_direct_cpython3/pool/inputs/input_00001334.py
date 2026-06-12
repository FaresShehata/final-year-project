"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""

from __future__ import annotations

import ast
import base64
import binascii
import csv
import hashlib
import hmac
import io
import itertools
import multiprocessing
import numbers
import os
import pathlib
import queue
import secrets
import string
import tempfile
import textwrap
import threading
import time
import tokenize
import contextlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import (
    Annotated, Callable, ClassVar, Concatenate, Coroutine, DefaultDict, Dict, Generator, Generic, Literal,
    NamedTuple, NonEmptySequence, ParamSpec, Protocol, Sequence, Set, Tuple, TypedDict, Union, cast)
from types import TracebackType
from typing_extensions import Self, TypeAlias, TypeGuard, Unpack, get_args, get_origin, get_type_hints
from collections.abc import AsyncGenerator, Awaitable


def _test_str():
    print('type: str')
    s1 = 'Hello world.'
    print(s1)
    s2 = """Hello \
        world."""
    print(s2)

    # f-strings
    name = 'Bob'
    age = 40
    print(f'{name} is {age}')

    # format()
    print('{} is {}'.format(name, age))

    # raise exception
    try:
        raise ValueError()
    except ValueError:
        pass

    # assert
    a: int = 1
    b: int = 2
    assert a == b, "a != b"

    with open('example.txt', 'w') as f:
        f.write('Hello World')

    with open('example.txt', 'r') as f:
        content = f.read()

    # readlines() returns list[str]
    lines = ['Hello', 'World']
    for line in lines:
        print(line)

    # enumerate() returns tuple[int, str]
    for index, line in enumerate(lines):
        print(index, line)


def _test_int():
    print('type: int')
    x = 0b1010 # binary literal
    y = 0o77 # octal literal
    z = 0x_Foo # hexadecimal literal
    w = 0xFF # octal literal
    u = 1_234 # underscore separated integer literals
    v = 1e10 # scientific notation (1 * 10^10)

    # conversion from other types to int
    d = int("42") # convert from string to int
    e = int(True) # convert from bool to int
    f = int([1, 2]) # convert from sequence to int
    g = int((1,)) # convert from tuple to int

    while True:
        try:
            x = input("Enter a number: ")
            break
        except KeyboardInterrupt:
            print('\nAborted.')
            exit()

    if isinstance(x, int):
        print('x is an int')
    elif isinstance(x, float):
        print('x is a float')


def _test_float():
    print('type: float')
    x = 0.5 # decimal literal
    y = .5 # decimal literal
    z = 5.0 # decimal literal
    w = 5. # decimal literal
    u = 5.e-1 # exponentiation operator
    v = 5e+1 # exponential operator
    # conversion from other types to float
    t = float(1) # convert from int to float
    s = float("inf") # positive infinity
    r = float("-inf") # negative infinity
    p = float("nan") # NaN value

    with open('example.txt', 'r') as f:
        content = f.readline()

    print(content.strip()) # strip newline character


def _test_complex():
    print('type: complex')
    x = 3 + 4j # real part and
def foo(x: MyAnnotatedClass) -> None:
    pass

foo(MyAnnotatedClass())

x: Annotated[type, "docstring"] | None = None # T is not annotated
y: Annotated[int, "docstring"] | None = None # T is an instance of type int
z: Annotated[bool, "docstring"] | None = None # T is an instance of type bool
a: Annotated[Tuple[int, int], "docstring"] | None = None # T is an instance of type tuple[int, int]
b: Annotated[Tuple[float, ...], "docstring"] | None = None # T is an instance of type tuple[float, ...]
c: Annotated[tuple[int, ...], "docstring"] | None = None # T is an instance of type tuple[int, ...]
d: Annotated[Union[int, str], "docstring"] | None = None # T is an instance of type Union[int, str]


def _test_bool():
    print('type: bool')
    x = False # boolean literal
    y = True # boolean literal
    z = 1 < 0 # comparison expression
    a = 1 > 0 or 0 < 0 # logical expression
    b = 1 == 1 # equality expression
    c = 1 != 0 # inequality expression
    d = 1 <= 1 # less than or equal expression
    e = 1 >= 1 # greater than or equal expression
    f = not 0 # negation expression
    g = 1 and 1 # conjunction expression
    h = 1 or 0 # disjunction expression
    i = 1 << 2 # bitwise shift left expression
    j = 1 >> 2 # bitwise shift right expression
    k = ~1 # bitwise complement expression
    l = 1 & 1 # bitwise AND expression
    m = 1 ^ 1 # bitwise XOR expression
    n = 1 | 1 # bitwise OR expression


def _test_list():
    print('type: list')
    # conversion from other types to list
    s = 'abcdefg' # string literal
    t = [ord(c) for c in s] # ord() converts each charater to its unicode code point
    u = list(t) # list() constructor creates a new list
    # copy by reference
    v = u # assign to alias
    v.append(ord('h')) # change element via alias
    print(u) # modify shared data
    # copy by value
    w = list(u) # use built-in function list() to make a copy
    w.append(ord('H'))
   # TODO: Create a class that has an attribute which is a dictionary with keys being strings and values being integers.
# Then create two methods:
# - one that sets a key-value pair if the key does not exist yet and another that updates the value corresponding to a given key by adding the argument passed as parameter.

class MyDictionary:
    def __init__(self):
        self.dict = {}

    def set_value_if_missing(self, key, value):
        if key not in self.dict.keys():
            self.dict[key] = value

    def update_value(self, key, value_to_add):
        if key in self.dict.keys():
            self.dict[key] += value_to_add
        else:
            print(f"Key '{key}' doesn't exist in the dictionary.")


my_dict = MyDictionary()
for i in range(5):
    my_dict.set_value_if_missing(random.randint(0, 9), random.randint(0, 9))
print(my_dict.dict)

my_dict.update_value(7, 4)
my_dict.update_value(6, 8)
print(my_dict.dict)