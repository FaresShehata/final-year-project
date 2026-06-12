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

T  = TypeVar("T")
P  = ParamSpec("P")

# ── TypeAlias ────────────────────────────────────────────────────────────────

JsonValue: TypeAlias = "int | float | str | bool | None | list[JsonValue] | dict[str, JsonValue]"
Seconds:   TypeAlias = float
Predicate: TypeAlias = Callable[[Any], bool]

# ── TypedDict ────────────────────────────────────────────────────────────────

class UserRecord(TypedDict, total=False):
    id:       int
    name:     str
    email:    str
    active:   bool
    metadata: dict[str, Any]


class MetricsRecord(TypedDict):
    latency_ms: float
    throughput: float
    error_rate: float
    count:     int


# ── TextWrap ────────────────────────────────────────────────────────────────

text_wrap = textwrap.dedent(
"""\
a = b"Hello, world!"
b = b'\x00Hello\x00world'
c = b'abc'.decode('utf-8')
d = bytes(b'abc', 'utf-8').decode()
e = '\u2713\u2713'.encode('utf-8')
f = '\\xab\\xbb'.encode('latin-1')
g = '\\x9d\\xa0'.encode('cp1125')
h = 'Hello, world!'
i = h.encode('iso-8859-1')

print(a)
print(b)
print(c)
print(d)
print(e)
print(f)
print(g)
print(h)
print(i)
""").strip()


# ── StringFormatter ─────────────────────────────────────────────────────────

class StringFormatter(NamedTuple):
    """
    >>> s = StringFormatter("{id}", {"id": 1})
    >>> print(s.format())
    1
    """

    template: str
    values:   dict[str, Any]

    def format(self) -> str:
        return self.template.format(**self.values)


def test_string_formatter():
    assert StringFormatter(template="{id}",
                           values={"id": 1}).format() == "1"


# ── Tokenize ────────────────────────────────────────────────────────────────

code_str = """\
for x in y:
    z += x
"""


def test_tokenization():
    tokens = list(tokenize.tokenize(io.BytesIO(code_str.encode()).readline))

    # First token should be the `for` keyword.
    assert tokens[0][0] == tokenize.NAME and tokens[0][1] == "for"

    # Second token should be an `identifier`, which is `x`.
    assert tokens[1][0] == tokenize.INDENT and tokens[1][1] == "x"

    # Third token should be a newline character.
    assert tokens[2][0] == tokenize.NEWLINE

    # Fourth token should be a `in` keyword.
    assert tokens[3][0] == tokenize.NAME and tokens[3][1] == "in"

    # Fifth token should be the identifier `y`.
    assert tokens[4][0] == tokenize.NAME and tokens[4][1]    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def level(self) -> int:
        return self.depth + (len(self.children) * 100)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} "
        + (" ".join([f'{k}={v}' for k, v in vars(self).items()]))
        + ">"


def create_tree(root: int | Node):
    nodes = [root]
    for i in range(len(nodes)):
        if isinstance(nodes[i], int):
            nodes.extend(Node(id=i, name=f"{nodes[i]}-{j}") for j in range(3))
            nodes[i].insert(nodes[-3])
            nodes[i].insert(nodes[-2])
            nodes[i].insert(nodes[-1])


if __name__ == "__main__":
    a = Node(id=0, name="A", depth=0)
   