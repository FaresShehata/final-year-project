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
    Annotated,
    Any,
    Callable,
    ClassVar,
    Final,
    Generic,
    Literal,
    NamedTuple,
    Never,
    ParamSpec,
    TypeAlias,
    TypedDict,
    TypeVar,
    get_type_hints,
)


def test_ast() -> None:
    """AST representation of a module with the given code."""
    source_code = """
    class Foo(object):
        def bar():
            pass
    """

    tree = ast.parse(source_code)
    print(ast.dump(tree))


def test_tokenize() -> None:
    """Tokenize a sequence of code tokens and display them in their original form.

    Use `token.ENCODING` to determine the encoding used for decoding the input.
    """
    filename = "test.txt"
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write("print('Hello World')")

    for token_info in tokenize.tokenize(open(filename).readline.__func__):
        print(token_info.string)


def test_textwrap() -> None:
    """Text wrap and fill operations."""
    sample_lines = ["This is a long string that will be split into multiple lines because no explicit linebreaks were provided.", "A second long string on the second line."]
    wrapped_lines = textwrap.wrap(sample_lines[0], width=20)
    print(wrapped_lines)

    print(textwrap.fill(sample_lines[1]))


class SampleFormatter(string.Formatter):

    def convert_field(
        self,
        value: str | object,
        conversion: str | None
    ) -> str | bytes | float | bool | int:

        if isinstance(value, str):
            return value.encode()

        return super().convert_field(value, conversion)


def test_string_formatter() -> None:
    """String Formatter API."""
    s = "[{id}] {name} has graduated from {school}"
    formatter = SampleFormatter()
    print(formatter.format(s, id='1', name='Joe', school='MIT'))


def test_typed_dict() -> None:
    """Typed dictionary example."""

    class Person(TypedDict):
        name: str
        age: int
        job: str

    person = {
        'name': 'John',
        'age': 30,
        'job': 'Engineer'
    }
    print(person['name'])


P = ParamSpec("P")
R = TypeVar("R")


class AsyncGenerator(Generic[P, R]):
    async def __aiter__(self) -> AsyncGenerator[Any]:
        while True:
            yield await self.__anext__()

    async def __aenter__(self) -> AsyncGenerator[Any]: ...     # pragma: nocover
    async def __aexit__(self, exc_type    """Minimal rational backed by integer numerator/denominator."""

    def __init__(self, num: int, den: int = 1):
        if den == 0:
            raise ZeroDivisionError
        g = _gcd(abs(num), abs(den))
        sign = -1 if den < 0 else 1
        self._n = sign * num // g
        self._d = sign * den // g

    # numbers.Rational interface
    @property
    def numerator(self) -> int:   return self._n
    @property
