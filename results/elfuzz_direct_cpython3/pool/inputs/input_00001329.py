"""
Seed 02 — async/await, Protocols, dataclasses, __slots__, structural pattern matching,
          walrus operator, typing generics, exception groups, ExceptionGroup
"""

from __future__ import annotations

import asyncio
import bisect
import dataclasses
import enum
import heapq
import json
import random
import re
import time
import types
import warnings
from abc import ABCMeta
from collections import (
    ChainMap,
    Counter,
    deque,
    OrderedDict,
    namedtuple,
    UserDict,
    UserList,
    UserString,
)
from concurrent.futures import Future as ConcurrentFuture
from contextlib import suppress
from functools import cached_property, partialmethod, reduce
from inspect import Parameter, Signature, signature
from itertools import chain, count, cycle
from pathlib import Path
from pprint import pprint
from string import ascii_letters, digits, punctuation
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from _typeshed import SupportsLessThan, SupportsRichComparison


def seed_01() -> None:
    """Primitives"""

    # Numeric literals
    print(42)  # Integer literal
    print(3.14)  # Floating point literal
    print(0b1010)  # Binary integer literal
    print(0o755)  # Octal integer literal
    print(0xFB)  # Hexadecimal integer literal
    print(-1e9)  # Scientific notation for floating-point literals
    print(0x_FF)  # The underscore character can be used to improve the readability of large numbers
    print(0b_, "0")  # An empty literal is not allowed in Python

    # String literals
    print("Hello world!")  # A string literal enclosed in single quotes
    print('He said, "I want to eat pizza."')  # A string literal enclosed in double quotes
    print(
        'She said, \'I want to eat pizza.\'"
    ')  # A string literal that contains both single and double quotes
    print(r"C:\Users\John\Documents")  # Raw string literal
    print("This\nis a\tnew line")
    print("""Multi-line
string
literal""")

    # Boolean literals
    print(True)  # True value
    print(False)  # False value
    print(not True)  # Negation
    print((not False) or (True))  # Logical operations
    print((False and True) == False)  # Comparison operators
    print((False or False) != True)  # Inequality operators
    print(("a" > "A") <= ("D" < "Z"))  # Relational operators
    print("apple" == "orange" >= "banana")  # Compound comparisons
    print(6 % 3 == 0)  # Modulo operation
    print(6 / 3 != 2)  # Division assignment operator
    print((6 // 3) << 1 == 8)  # Bitwise operators
    print(6 & 3 == 0)  # Bitwise AND operator
    print(6 | 3 == 7)  # Bitwise OR operator
    print(6 ^ 3 == 5)  # Bitwise XOR operator
    print(~0xF == -6)  # Bitwise NOT operator
    print(6 ** 3 == 216)  # Exponentiation operator
    print(((6 ** 3) // 10) + ((6 * 6) - 10))