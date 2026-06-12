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
R  = RevealType[T]
S  = SupportsIndex | SupportsFloat
Seconds   : Final[Literal[1]] = 1
Milliseconds: Final[Literal[0.001]] = 0.001
Microseconds: Final[Literal[0.000_001]] = 0.000_001
Nanoseconds: Final[Literal[0.000_000_001]] = 0.000_000_001
Picoseconds: Final[Literal[0.000_000_000_001]] = 0.000_000_000_001


def generate_password(length: int) -> str:
    return "".join(secrets.choice(string.ascii_letters + string.digits)
                   for _ in range(length))


def parse_csv() -> None:
    with open(pathlib.Path(__file__).parent / "seed_data.csv") as file:
        reader = csv.reader(file)
        print(*next(reader), sep=", ")
        print(*list(itertools.islice(reader, 8)), sep="\n")


# https://peps.python.org/pep-0639/
class MultipartFormData(NamedTuple):
    content_type: str
    data: bytes
    filename: str


def write_multipart_form_data_to_file(
    multipart_form_data: MultipartFormData,
    path: pathlib.Path,
) -> None:
    with open(path, "wb+") as f:
        f.write(multipart_form_data.data)


def create_parts_from_file_list(
    files: list[pathlib.Path],
) -> list[MultipartFormData]:
    return [
        MultipartFormData(content_type="application/octet-stream", data=f.read(), filename=file.name)
        for file in files
    ]


def main() -> None:
    parse_csv()

    # https://docs.python.org/3/library/tokenize.html
    print(tokenize.tokenize(io.BytesIO(b"hello world\n").readline))

    # https://www.geeksforgeeks.org/python-string-formatter-module/
    fmt_str = "{name} is {age:d} years old."
    print(fmt_str.format(name="Alice", age=28))
    print(textwrap.fill(fmt_str, width=20))



if __name__ == "__main__":
    main()